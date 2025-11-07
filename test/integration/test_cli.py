"""Integration tests for CLI functionality."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory, NamedTemporaryFile
from unittest.mock import patch

from click.testing import CliRunner

from cli.main import main


class TestCLIConfigHandling:
    """Test CLI configuration loading and validation."""
    
    def test_cli_loads_default_config_file(self):
        """Should load config from ./config.json by default."""
        config_data = {
            "collection_name": "test-collection",
            "source_dir": "/tmp/nonexistent",
            "dest_dir": "/tmp/dest"
        }
        
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            with patch('lib.model.config.Config.get_default_config_path', return_value=config_path):
                runner = CliRunner()
                result = runner.invoke(main, [])
                
                # Should fail due to source directory not existing, but config should load successfully
                assert "Source directory does not exist" in result.output
                assert result.exit_code == 1
    
    def test_cli_loads_custom_config_file(self):
        """Should load config from custom path when --config specified."""
        config_data = {
            "collection_name": "custom-collection",
            "source_dir": "/tmp/nonexistent",
            "dest_dir": "/tmp/dest"
        }
        
        with TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / "custom.json"
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            runner = CliRunner()
            result = runner.invoke(main, ['--config', str(config_path)])
            
            # Should fail due to source directory not existing, but custom config should load
            assert "Source directory does not exist" in result.output
            assert result.exit_code == 1
    
    def test_cli_handles_missing_config_file(self):
        """Should display error when config file doesn't exist."""
        runner = CliRunner()
        result = runner.invoke(main, ['--config', '/does/not/exist.json'])
        
        # Click handles this validation before our code runs
        assert "does not exist" in result.output
        assert result.exit_code == 2
    
    def test_cli_handles_invalid_json_config(self):
        """Should display error when config file has invalid JSON."""
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"invalid": json}')
            config_path = Path(f.name)
        
        try:
            runner = CliRunner()
            result = runner.invoke(main, ['--config', str(config_path)])
            
            assert result.exit_code == 1
            # Should contain some kind of JSON error message
            assert "json" in result.output.lower() or "invalid" in result.output.lower()
        finally:
            config_path.unlink()
    
    def test_cli_handles_missing_required_config_fields(self):
        """Should display error when required config fields are missing."""
        config_data = {
            "collection_name": "test"
            # Missing source_dir and dest_dir
        }
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            runner = CliRunner()
            result = runner.invoke(main, ['--config', str(config_path)])
            
            assert "Missing required configuration fields" in result.output
            assert result.exit_code == 1
        finally:
            config_path.unlink()


class TestCLIFlags:
    """Test CLI flag functionality."""
    
    def test_verbose_flag_shows_additional_output(self):
        """Should show additional output when --verbose flag is used."""
        with TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source" 
            source_dir.mkdir()  # Create the source directory so validation passes
            
            config_data = {
                "collection_name": "test-collection",
                "source_dir": str(source_dir),
                "dest_dir": str(Path(temp_dir) / "dest")
            }
            
            config_path = Path(temp_dir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            runner = CliRunner()
            result = runner.invoke(main, ['--config', str(config_path), '--verbose'])
            
            # Verbose should show config loading and source/dest info
            assert "Loading configuration from:" in result.output
            assert "Source directory:" in result.output
            assert "Destination directory:" in result.output
            assert "Collection:" in result.output
    
    def test_dry_run_flag_shows_dry_run_message(self):
        """Should show dry run message when --dry-run flag is used."""
        with TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            source_dir.mkdir()  # Create the source directory so validation passes
            
            config_data = {
                "collection_name": "test-collection",
                "source_dir": str(source_dir),
                "dest_dir": str(Path(temp_dir) / "dest")
            }
            
            config_path = Path(temp_dir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            runner = CliRunner()
            result = runner.invoke(main, ['--config', str(config_path), '--dry-run', '--verbose'])
            
            assert "DRY RUN MODE - no symlinks will be created" in result.output
    
    def test_force_flag_overrides_config(self):
        """Should override config.force_reprocess when --force flag is used."""
        # This test verifies the flag is passed through - actual force behavior 
        # would be tested in photo_manager tests
        config_data = {
            "collection_name": "test-collection",
            "source_dir": "/tmp/nonexistent",
            "dest_dir": "/tmp/dest",
            "force_reprocess": False
        }
        
        with NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = Path(f.name)
        
        try:
            runner = CliRunner()
            # Just verify the flag doesn't cause errors - actual force logic is in photo_manager
            result = runner.invoke(main, ['--config', str(config_path), '--force'])
            
            # Should still fail on missing source directory
            assert "Source directory does not exist" in result.output
            assert result.exit_code == 1
        finally:
            config_path.unlink()


class TestCLIIntegrationWithPhotoManager:
    """Test CLI integration with photo processing."""
    
    def test_cli_processes_photos_successfully(self):
        """Should process photos and display summary when everything is configured correctly."""
        with TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            dest_dir = Path(temp_dir) / "dest"
            source_dir.mkdir()
            
            # Create a test image file (empty file with .jpg extension)
            test_image = source_dir / "test.jpg"
            test_image.touch()
            
            config_data = {
                "collection_name": "test-collection",
                "source_dir": str(source_dir),
                "dest_dir": str(dest_dir),
                "collection_description": "Test collection"
            }
            
            config_path = Path(temp_dir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            runner = CliRunner()
            result = runner.invoke(main, ['--config', str(config_path)])
            
            # Should process successfully and show summary
            assert result.exit_code == 0
            assert "Processed 1 pics" in result.output
            assert "0 warnings" in result.output  # TODO: Update when warnings are implemented
            assert "0 errors" in result.output    # TODO: Update when errors are implemented
            
            # Should create manifest file
            assert (dest_dir / "manifest.json").exists()
    
    def test_cli_dry_run_creates_dryrun_manifest(self):
        """Should create .dryrun.json manifest file in dry-run mode."""
        with TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            dest_dir = Path(temp_dir) / "dest"
            source_dir.mkdir()
            
            # Create a test image file
            test_image = source_dir / "test.jpg"
            test_image.touch()
            
            config_data = {
                "collection_name": "test-collection",
                "source_dir": str(source_dir),
                "dest_dir": str(dest_dir)
            }
            
            config_path = Path(temp_dir) / "config.json"
            with open(config_path, 'w') as f:
                json.dump(config_data, f)
            
            runner = CliRunner()
            result = runner.invoke(main, ['--config', str(config_path), '--dry-run', '--verbose'])
            
            assert result.exit_code == 0
            assert "Processed 1 pics" in result.output
            assert "manifest.dryrun.json" in result.output
            
            # Should create dry-run manifest, not regular manifest
            assert (dest_dir / "manifest.dryrun.json").exists()
            assert not (dest_dir / "manifest.json").exists()
    
    def test_cli_help_displays_usage_information(self):
        """Should display help information when --help flag is used."""
        runner = CliRunner()
        result = runner.invoke(main, ['--help'])
        
        assert result.exit_code == 0
        assert "Organize and rename photo collections" in result.output
        assert "--config" in result.output
        assert "--dry-run" in result.output
        assert "--verbose" in result.output
        assert "--force" in result.output