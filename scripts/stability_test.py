#!/usr/bin/env python3
"""48-hour GAAS stability test"""
import sys
import time
import subprocess
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
from loguru import logger
import threading
import psutil
import os

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

class StabilityTest:
    def __init__(self, duration_hours=48):
        self.duration_hours = duration_hours
        self.duration_seconds = duration_hours * 3600
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=duration_hours)

        # Test statistics
        self.stats = {
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'gaas_restarts': 0,
            'web_restarts': 0,
            'memory_samples': [],
            'disk_samples': [],
            'response_times': [],
            'errors': []
        }

        logger.info(f"Starting {duration_hours}-hour stability test")
        logger.info(f"Start time: {self.start_time}")
        logger.info(f"End time: {self.end_time}")

    def check_service_health(self):
        """Check if GAAS services are healthy"""
        try:
            # Check GAAS main service
            gaas_status = subprocess.run(
                ['systemctl', 'is-active', 'gaas'],
                capture_output=True, text=True
            )

            # Check GAAS web service
            web_status = subprocess.run(
                ['systemctl', 'is-active', 'gaas-web'],
                capture_output=True, text=True
            )

            # Check web endpoint
            try:
                response = requests.get('http://localhost:8000/health', timeout=10)
                web_healthy = response.status_code == 200
            except:
                web_healthy = False

            return {
                'gaas_active': gaas_status.stdout.strip() == 'active',
                'web_active': web_status.stdout.strip() == 'active',
                'web_healthy': web_healthy,
                'gaas_status': gaas_status.stdout.strip(),
                'web_status': web_status.stdout.strip()
            }
        except Exception as e:
            return {'error': str(e)}

    def collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            # Memory usage
            memory = psutil.virtual_memory()
            self.stats['memory_samples'].append({
                'timestamp': datetime.now().isoformat(),
                'total_gb': memory.total / (1024**3),
                'used_gb': memory.used / (1024**3),
                'percent': memory.percent
            })

            # Disk usage
            disk = psutil.disk_usage('/home/ubuntu')
            self.stats['disk_samples'].append({
                'timestamp': datetime.now().isoformat(),
                'total_gb': disk.total / (1024**3),
                'used_gb': disk.used / (1024**3),
                'percent': (disk.used / disk.total) * 100
            })

            # GAAS process metrics
            try:
                gaas_process = None
                for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                    if proc.info['cmdline'] and 'gaas_unified.py' in ' '.join(proc.info['cmdline']):
                        gaas_process = proc
                        break

                if gaas_process:
                    gaas_process.memory_info()
            except:
                pass

        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

    def test_api_response_times(self):
        """Test API response times"""
        endpoints = [
            'http://localhost:8000/health',
            'http://localhost:8000/api/nba/summary',
            'http://localhost:8000/api/nhl/latest'
        ]

        for endpoint in endpoints:
            try:
                start_time = time.time()
                response = requests.get(endpoint, timeout=30)
                end_time = time.time()

                response_time = end_time - start_time
                self.stats['response_times'].append({
                    'endpoint': endpoint,
                    'response_time': response_time,
                    'status_code': response.status_code,
                    'timestamp': datetime.now().isoformat()
                })

            except Exception as e:
                self.stats['response_times'].append({
                    'endpoint': endpoint,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

    def restart_service_if_needed(self, health):
        """Restart services if they're not healthy"""
        if 'error' in health:
            logger.error(f"Health check error: {health['error']}")
            return False

        services_restarted = False

        # Restart GAAS service if needed
        if not health['gaas_active']:
            logger.warning("GAAS service is not active, restarting...")
            try:
                subprocess.run(['sudo', 'systemctl', 'restart', 'gaas'], check=True)
                self.stats['gaas_restarts'] += 1
                services_restarted = True
                logger.info("GAAS service restarted")
            except Exception as e:
                logger.error(f"Failed to restart GAAS: {e}")

        # Restart web service if needed
        if not health['web_active']:
            logger.warning("GAAS web service is not active, restarting...")
            try:
                subprocess.run(['sudo', 'systemctl', 'restart', 'gaas-web'], check=True)
                self.stats['web_restarts'] += 1
                services_restarted = True
                logger.info("GAAS web service restarted")
            except Exception as e:
                logger.error(f"Failed to restart web: {e}")

        return services_restarted

    def run_test_cycle(self):
        """Run a single test cycle"""
        cycle_start = datetime.now()
        self.stats['total_checks'] += 1

        # Check service health
        health = self.check_service_health()

        # Log health status
        if 'error' not in health:
            logger.info(f"Health check - GAAS: {health['gaas_status']}, Web: {health['web_status']}, Web Healthy: {health['web_healthy']}")

            if health['gaas_active'] and health['web_active'] and health['web_healthy']:
                self.stats['successful_checks'] += 1
            else:
                self.stats['failed_checks'] += 1
                self.stats['errors'].append({
                    'timestamp': cycle_start.isoformat(),
                    'health': health
                })
        else:
            self.stats['failed_checks'] += 1
            self.stats['errors'].append({
                'timestamp': cycle_start.isoformat(),
                'error': health['error']
            })

        # Collect system metrics
        self.collect_system_metrics()

        # Test API response times
        self.test_api_response_times()

        # Restart services if needed
        self.restart_service_if_needed(health)

        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        logger.debug(f"Test cycle completed in {cycle_duration:.2f}s")

    def generate_report(self):
        """Generate final stability report"""
        elapsed_time = (datetime.now() - self.start_time).total_seconds() / 3600

        report = {
            'test_duration_hours': elapsed_time,
            'start_time': self.start_time.isoformat(),
            'end_time': datetime.now().isoformat(),
            'summary': self.stats,
            'success_rate': (self.stats['successful_checks'] / self.stats['total_checks'] * 100) if self.stats['total_checks'] > 0 else 0,
        }

        # Calculate statistics
        if self.stats['memory_samples']:
            avg_memory = sum(s['percent'] for s in self.stats['memory_samples']) / len(self.stats['memory_samples'])
            max_memory = max(s['percent'] for s in self.stats['memory_samples'])
            report['avg_memory_percent'] = avg_memory
            report['max_memory_percent'] = max_memory

        if self.stats['disk_samples']:
            avg_disk = sum(s['percent'] for s in self.stats['disk_samples']) / len(self.stats['disk_samples'])
            max_disk = max(s['percent'] for s in self.stats['disk_samples'])
            report['avg_disk_percent'] = avg_disk
            report['max_disk_percent'] = max_disk

        if self.stats['response_times']:
            # Filter successful responses only
            successful_responses = [r for r in self.stats['response_times'] if 'response_time' in r]
            if successful_responses:
                avg_response_time = sum(r['response_time'] for r in successful_responses) / len(successful_responses)
                max_response_time = max(r['response_time'] for r in successful_responses)
                report['avg_response_time'] = avg_response_time
                report['max_response_time'] = max_response_time

        return report

    def run(self):
        """Run the stability test"""
        logger.info("Starting stability test cycles...")

        try:
            while datetime.now() < self.end_time:
                cycle_start = time.time()

                # Run test cycle
                self.run_test_cycle()

                # Calculate remaining time and sleep interval
                now = datetime.now()
                remaining_seconds = (self.end_time - now).total_seconds()

                # Run checks every 5 minutes
                sleep_interval = min(300, remaining_seconds)

                if remaining_seconds <= 0:
                    break

                # Sleep until next check or end of test
                logger.debug(f"Sleeping for {sleep_interval} seconds...")
                time.sleep(sleep_interval)

        except KeyboardInterrupt:
            logger.info("Test interrupted by user")
        except Exception as e:
            logger.error(f"Test failed with error: {e}")

        # Generate and save final report
        logger.info("Generating stability test report...")
        report = self.generate_report()

        # Save report
        report_file = Path(f"stability_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        logger.info("="*60)
        logger.info("STABILITY TEST SUMMARY")
        logger.info("="*60)
        logger.info(f"Duration: {report['test_duration_hours']:.2f} hours")
        logger.info(f"Success Rate: {report['success_rate']:.1f}%")
        logger.info(f"Total Checks: {self.stats['total_checks']}")
        logger.info(f"Successful: {self.stats['successful_checks']}")
        logger.info(f"Failed: {self.stats['failed_checks']}")
        logger.info(f"GAAS Restarts: {self.stats['gaas_restarts']}")
        logger.info(f"Web Restarts: {self.stats['web_restarts']}")

        if 'avg_memory_percent' in report:
            logger.info(f"Avg Memory: {report['avg_memory_percent']:.1f}%")
            logger.info(f"Max Memory: {report['max_memory_percent']:.1f}%")

        if 'avg_disk_percent' in report:
            logger.info(f"Avg Disk: {report['avg_disk_percent']:.1f}%")
            logger.info(f"Max Disk: {report['max_disk_percent']:.1f}%")

        if 'avg_response_time' in report:
            logger.info(f"Avg Response Time: {report['avg_response_time']:.2f}s")
            logger.info(f"Max Response Time: {report['max_response_time']:.2f}s")

        logger.info(f"Report saved to: {report_file}")
        logger.info("="*60)

        return report


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='GAAS Stability Test')
    parser.add_argument('--duration', type=int, default=48, help='Test duration in hours')
    parser.add_argument('--quick', action='store_true', help='Run quick 10-minute test')

    args = parser.parse_args()

    # Quick test mode
    if args.quick:
        duration = 10/60  # 10 minutes in hours
        test = StabilityTest(duration_hours=duration)
    else:
        test = StabilityTest(duration_hours=args.duration)

    try:
        report = test.run()

        # Return exit code based on success rate
        success_rate = report['success_rate']
        if success_rate >= 95:
            logger.info("✅ Stability test PASSED")
            sys.exit(0)
        elif success_rate >= 80:
            logger.warning("⚠️ Stability test MARGINAL")
            sys.exit(1)
        else:
            logger.error("❌ Stability test FAILED")
            sys.exit(2)

    except Exception as e:
        logger.error(f"Stability test crashed: {e}")
        sys.exit(3)


if __name__ == "__main__":
    main()