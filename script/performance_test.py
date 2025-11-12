#!/usr/bin/env python3
"""Performance measurement script for NormPic on real-world photo collections.

This script runs NormPic with detailed performance monitoring and generates
comprehensive analysis of memory usage, processing time, and system resources.

Usage:
    1. Copy config.local.template.json to config.local.json
    2. Edit config.local.json with your actual photo collection paths  
    3. Run: uv run script/performance_test.py
    
For web-optimized collection comparison:
    1. Copy config to config.local.web.json and edit paths
    2. Run: uv run script/performance_test.py config.local.web.json
"""

import json
import time
import psutil
import platform
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class SystemInfo:
    """System hardware and environment information."""
    cpu_model: str
    cpu_cores: int
    cpu_threads: int
    ram_total_gb: float
    storage_type: str  # SSD/HDD/Unknown
    os_name: str
    os_version: str
    python_version: str
    git_commit: Optional[str]


@dataclass
class ImageSizeStats:
    """Image size statistics for the collection."""
    avg_size_mb: float
    median_size_mb: float
    min_size_mb: float
    max_size_mb: float
    total_size_gb: float
    size_ranges: Dict[str, int]  # e.g., "0-1MB": count, "1-5MB": count, etc.


@dataclass
class PerformanceMetrics:
    """Performance measurement results."""
    total_time_seconds: float
    peak_memory_mb: float
    avg_memory_mb: float
    cpu_percent_avg: float
    photos_processed: int
    photos_per_second: float
    total_source_size_gb: float
    manifest_size_kb: float
    errors: int
    warnings: int
    image_stats: ImageSizeStats


@dataclass
class BenchmarkResult:
    """Complete benchmark result with system info and metrics."""
    system_info: SystemInfo
    config_used: Dict[str, Any]
    performance: PerformanceMetrics
    timestamp: str


class PerformanceMonitor:
    """Monitor system resources during NormPic execution."""
    
    def __init__(self):
        self.process = psutil.Process()
        self.memory_samples: List[float] = []
        self.cpu_samples: List[float] = []
        self.monitoring = False
        
    def start_monitoring(self):
        """Start collecting performance samples."""
        self.monitoring = True
        self.memory_samples = []
        self.cpu_samples = []
        
    def sample_resources(self):
        """Collect current resource usage sample."""
        if self.monitoring:
            try:
                memory_mb = self.process.memory_info().rss / 1024 / 1024
                cpu_percent = self.process.cpu_percent()
                self.memory_samples.append(memory_mb)
                self.cpu_samples.append(cpu_percent)
            except psutil.NoSuchProcess:
                pass  # Process may have ended
                
    def stop_monitoring(self):
        """Stop monitoring and return results."""
        self.monitoring = False
        
    def get_metrics(self) -> tuple[float, float, float]:
        """Get peak memory, average memory, and average CPU usage."""
        if not self.memory_samples:
            return 0.0, 0.0, 0.0
            
        peak_memory = max(self.memory_samples)
        avg_memory = sum(self.memory_samples) / len(self.memory_samples)
        avg_cpu = sum(self.cpu_samples) / len(self.cpu_samples) if self.cpu_samples else 0.0
        
        return peak_memory, avg_memory, avg_cpu


def get_system_info() -> SystemInfo:
    """Collect comprehensive system information."""
    # CPU information
    cpu_info = platform.processor() or "Unknown"
    cpu_cores = psutil.cpu_count(logical=False) or 0
    cpu_threads = psutil.cpu_count(logical=True) or 0
    
    # Memory information
    memory = psutil.virtual_memory()
    ram_gb = memory.total / (1024**3)
    
    # Storage type detection (basic heuristic)
    storage_type = "Unknown"
    try:
        # Try to detect SSD vs HDD (Linux-specific approach)
        result = subprocess.run(['lsblk', '-d', '-o', 'name,rota'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0 and '0' in result.stdout:
            storage_type = "SSD"
        elif result.returncode == 0 and '1' in result.stdout:
            storage_type = "HDD"
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    # OS information
    os_name = platform.system()
    os_version = platform.release()
    python_version = platform.python_version()
    
    # Git commit hash
    git_commit = None
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            git_commit = result.stdout.strip()[:12]  # Short hash
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    return SystemInfo(
        cpu_model=cpu_info,
        cpu_cores=cpu_cores,
        cpu_threads=cpu_threads,
        ram_total_gb=ram_gb,
        storage_type=storage_type,
        os_name=os_name,
        os_version=os_version,
        python_version=python_version,
        git_commit=git_commit
    )


def analyze_image_sizes(source_dir: Path) -> ImageSizeStats:
    """Analyze image file sizes in the source directory."""
    image_extensions = {'.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp', '.webp', '.heic', '.raw'}
    sizes_mb = []
    
    print(f"Analyzing image sizes in {source_dir}...")
    
    try:
        for file_path in source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in image_extensions:
                size_mb = file_path.stat().st_size / (1024 * 1024)
                sizes_mb.append(size_mb)
    except (OSError, PermissionError) as e:
        print(f"Warning: Could not analyze some files: {e}")
    
    if not sizes_mb:
        return ImageSizeStats(0, 0, 0, 0, 0, {})
    
    sizes_mb.sort()
    total_size_gb = sum(sizes_mb) / 1024
    
    # Calculate statistics
    avg_size = sum(sizes_mb) / len(sizes_mb)
    median_size = sizes_mb[len(sizes_mb) // 2]
    min_size = min(sizes_mb)
    max_size = max(sizes_mb)
    
    # Create size range buckets
    ranges = {
        "0-1MB": 0,
        "1-5MB": 0, 
        "5-10MB": 0,
        "10-25MB": 0,
        "25-50MB": 0,
        "50MB+": 0
    }
    
    for size in sizes_mb:
        if size < 1:
            ranges["0-1MB"] += 1
        elif size < 5:
            ranges["1-5MB"] += 1
        elif size < 10:
            ranges["5-10MB"] += 1
        elif size < 25:
            ranges["10-25MB"] += 1
        elif size < 50:
            ranges["25-50MB"] += 1
        else:
            ranges["50MB+"] += 1
    
    return ImageSizeStats(
        avg_size_mb=avg_size,
        median_size_mb=median_size,
        min_size_mb=min_size,
        max_size_mb=max_size,
        total_size_gb=total_size_gb,
        size_ranges=ranges
    )


def run_normpic_with_monitoring(config_file: Path, dry_run: bool = False) -> PerformanceMetrics:
    """Run NormPic CLI with comprehensive performance monitoring."""
    
    # Load config to get paths for analysis
    with open(config_file) as f:
        config_data = json.load(f)
    
    source_dir = Path(config_data['source_dir']).expanduser()
    dest_dir = Path(config_data['dest_dir']).expanduser()
    
    # Ensure destination directory exists
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Analyze image sizes before processing
    image_stats = analyze_image_sizes(source_dir)
    
    print(f"Collection size: {image_stats.total_size_gb:.2f} GB")
    print("Starting NormPic with performance monitoring...")
    
    # Build CLI command using the main entry point with expanded paths
    cmd = ['uv', 'run', 'python', 'main.py', 
           '--source-dir', str(source_dir),
           '--dest-dir', str(dest_dir),
           '--collection-name', config_data['collection_name'],
           '--verbose']
    if dry_run:
        cmd.append('--dry-run')
    
    start_time = time.time()
    
    # Start process and monitor
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Monitor the subprocess
        monitor = PerformanceMonitor()
        monitor.process = psutil.Process(process.pid)
        monitor.start_monitoring()
        
        # Poll process and sample resources
        while process.poll() is None:
            monitor.sample_resources()
            time.sleep(0.1)  # Sample every 100ms
        
        # Get final output
        stdout, stderr = process.communicate()
        return_code = process.returncode
        
    finally:
        end_time = time.time()
        monitor.stop_monitoring()
    
    total_time = end_time - start_time
    peak_memory, avg_memory, avg_cpu = monitor.get_metrics()
    
    # Parse output for photo count and errors
    photos_processed = 0
    errors = 0
    warnings = 0
    
    if return_code == 0 and stdout:
        # Look for "Processed X pics" in output
        import re
        match = re.search(r'Processed (\d+) pics, (\d+) warnings, (\d+) errors', stdout)
        if match:
            photos_processed = int(match.group(1))
            warnings = int(match.group(2))
            errors = int(match.group(3))
    else:
        print(f"NormPic failed with return code {return_code}")
        if stderr:
            print(f"Error output: {stderr}")
    
    # Calculate manifest size
    manifest_file = "manifest.dryrun.json" if dry_run else "manifest.json"
    manifest_path = dest_dir / manifest_file
    manifest_size_kb = 0
    if manifest_path.exists():
        manifest_size_kb = manifest_path.stat().st_size / 1024
    
    photos_per_second = photos_processed / total_time if total_time > 0 else 0
    
    performance = PerformanceMetrics(
        total_time_seconds=total_time,
        peak_memory_mb=peak_memory,
        avg_memory_mb=avg_memory,
        cpu_percent_avg=avg_cpu,
        photos_processed=photos_processed,
        photos_per_second=photos_per_second,
        total_source_size_gb=image_stats.total_size_gb,
        manifest_size_kb=manifest_size_kb,
        errors=errors,
        warnings=warnings,
        image_stats=image_stats
    )
    
    return performance


def analyze_manifest(manifest_path: Path) -> Dict[str, Any]:
    """Analyze the generated manifest for insights."""
    if not manifest_path.exists():
        return {"error": "Manifest file not found"}
    
    try:
        with open(manifest_path) as f:
            manifest_data = json.load(f)
        
        pics = manifest_data.get('pics', [])
        analysis = {
            "total_pics": len(pics),
            "cameras_found": len(set(pic.get('camera', 'Unknown') for pic in pics)),
            "timestamp_sources": {},
            "file_extensions": {},
            "size_distribution": {
                "min_mb": 0,
                "max_mb": 0,
                "avg_mb": 0
            }
        }
        
        # Analyze timestamp sources
        for pic in pics:
            source = pic.get('timestamp_source', 'Unknown')
            analysis["timestamp_sources"][source] = analysis["timestamp_sources"].get(source, 0) + 1
        
        # Analyze file extensions
        for pic in pics:
            filename = pic.get('dest_filename', '')
            if '.' in filename:
                ext = filename.split('.')[-1].lower()
                analysis["file_extensions"][ext] = analysis["file_extensions"].get(ext, 0) + 1
        
        # Analyze file sizes
        sizes_mb = [pic.get('size_bytes', 0) / (1024*1024) for pic in pics if pic.get('size_bytes')]
        if sizes_mb:
            analysis["size_distribution"] = {
                "min_mb": min(sizes_mb),
                "max_mb": max(sizes_mb),
                "avg_mb": sum(sizes_mb) / len(sizes_mb)
            }
        
        return analysis
        
    except (json.JSONDecodeError, KeyError) as e:
        return {"error": f"Failed to analyze manifest: {e}"}


def save_benchmark_result(result: BenchmarkResult, output_file: Path):
    """Save benchmark result to JSON file."""
    with open(output_file, 'w') as f:
        json.dump(asdict(result), f, indent=2, default=str)
    print(f"Benchmark results saved to: {output_file}")


def print_performance_summary(result: BenchmarkResult, manifest_analysis: Dict[str, Any]):
    """Print a human-readable performance summary."""
    sys_info = result.system_info
    perf = result.performance
    img_stats = perf.image_stats
    
    print("\n" + "="*60)
    print("NORMPIC PERFORMANCE BENCHMARK RESULTS")
    print("="*60)
    
    print("\nSystem Information:")
    print(f"  CPU: {sys_info.cpu_model}")
    print(f"  Cores/Threads: {sys_info.cpu_cores}/{sys_info.cpu_threads}")
    print(f"  RAM: {sys_info.ram_total_gb:.1f} GB")
    print(f"  Storage: {sys_info.storage_type}")
    print(f"  OS: {sys_info.os_name} {sys_info.os_version}")
    print(f"  Python: {sys_info.python_version}")
    if sys_info.git_commit:
        print(f"  Git Commit: {sys_info.git_commit}")
    
    print("\nCollection Information:")
    print(f"  Name: {result.config_used['collection_name']}")
    print(f"  Total Size: {perf.total_source_size_gb:.2f} GB")
    print(f"  Photos Processed: {perf.photos_processed:,}")
    
    print("\nImage Size Statistics:")
    print(f"  Average: {img_stats.avg_size_mb:.1f} MB")
    print(f"  Median: {img_stats.median_size_mb:.1f} MB") 
    print(f"  Range: {img_stats.min_size_mb:.1f} - {img_stats.max_size_mb:.1f} MB")
    print("  Size Distribution:")
    total_images = sum(img_stats.size_ranges.values())
    for size_range, count in img_stats.size_ranges.items():
        if count > 0:
            percentage = (count / total_images) * 100 if total_images > 0 else 0
            print(f"    {size_range}: {count:,} ({percentage:.1f}%)")
    
    print("\nPerformance Metrics:")
    print(f"  Total Time: {perf.total_time_seconds:.2f} seconds")
    print(f"  Photos/Second: {perf.photos_per_second:.1f}")
    mb_per_sec = (perf.total_source_size_gb * 1024) / perf.total_time_seconds if perf.total_time_seconds > 0 else 0
    print(f"  MB/Second: {mb_per_sec:.1f}")
    print(f"  Peak Memory: {perf.peak_memory_mb:.1f} MB")
    print(f"  Average Memory: {perf.avg_memory_mb:.1f} MB")
    print(f"  Average CPU: {perf.cpu_percent_avg:.1f}%")
    print(f"  Manifest Size: {perf.manifest_size_kb:.1f} KB")
    
    if manifest_analysis and "error" not in manifest_analysis:
        print("\nManifest Analysis:")
        print(f"  Cameras Found: {manifest_analysis['cameras_found']}")
        print(f"  File Types: {', '.join(manifest_analysis['file_extensions'].keys())}")
        if manifest_analysis['timestamp_sources']:
            print(f"  Timestamp Sources: {', '.join(manifest_analysis['timestamp_sources'].keys())}")
    
    print("\n" + "="*60)


def main():
    """Main performance testing workflow."""
    # Handle command line argument for config file
    config_filename = "config.local.json"
    if len(sys.argv) > 1:
        config_filename = sys.argv[1]
    
    config_file = Path(config_filename)
    
    if not config_file.exists():
        print(f"Error: {config_file} not found!")
        if config_filename == "config.local.json":
            print("Please copy config.local.template.json to config.local.json")
            print("and edit it with your actual photo collection paths.")
            print("\nFor web-optimized collection:")
            print("1. Copy config.local.json to config.local.web.json") 
            print("2. Edit paths to point to web-optimized images")
            print("3. Run: uv run script/performance_test.py config.local.web.json")
        sys.exit(1)
    
    try:
        # Load configuration to display info
        with open(config_file) as f:
            config_data = json.load(f)
        
        print("Loading configuration...")
        print(f"Configuration loaded from: {config_file}")
        print(f"  Source: {config_data['source_dir']}")
        print(f"  Destination: {config_data['dest_dir']}")
        print(f"  Collection: {config_data['collection_name']}")
        
        # Gather system information
        print("\nGathering system information...")
        system_info = get_system_info()
        
        # Run performance benchmark
        print("\nRunning NormPic performance benchmark...")
        performance = run_normpic_with_monitoring(config_file, dry_run=False)
        
        # Analyze results
        manifest_file = Path(config_data['dest_dir']) / "manifest.json"
        manifest_analysis = analyze_manifest(manifest_file)
        
        # Create benchmark result
        result = BenchmarkResult(
            system_info=system_info,
            config_used=config_data,
            performance=performance,
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # Generate output filename based on config
        config_name = config_file.stem.replace('.', '_')
        output_file = Path(f"performance_results_{config_name}.json")
        
        # Save and display results
        save_benchmark_result(result, output_file)
        print_performance_summary(result, manifest_analysis)
        
        # Suggest next steps
        print("\nNext Steps:")
        print(f"1. Review the generated manifest at: {manifest_file}")
        print("2. Compare results between full and web collections")
        print("3. Use these results to create doc/analysis/performance.md")
        print(f"4. Results saved to: {output_file}")
        
    except Exception as e:
        print(f"Error during performance testing: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()