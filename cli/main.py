"""NormPic CLI - Photo organization and manifest generation."""

import sys
from pathlib import Path
from typing import Optional

import click

from src.model.config import Config
from src.manager.photo_manager import organize_photos
from src.manager.config_manager import load_config_with_full_precedence


@click.command()
@click.option(
    "--config",
    "config_path",
    type=click.Path(exists=True, path_type=Path),
    default=None,
    help="Path to configuration file (default: ./config.json)",
)
@click.option(
    "--dry-run", is_flag=True, help="Generate manifest without creating symlinks"
)
@click.option("--verbose", is_flag=True, help="Show each photo being processed")
@click.option("--force", is_flag=True, help="Reprocess everything ignoring cache")
@click.option(
    "--source-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Source directory containing photos (overrides config file and env)"
)
@click.option(
    "--dest-dir", 
    type=click.Path(file_okay=False, path_type=Path),
    default=None,
    help="Destination directory for organized photos (overrides config file and env)"
)
@click.option(
    "--collection-name",
    type=str,
    default=None,
    help="Collection name for photo filenames (overrides config file and env)"
)
def main(
    config_path: Optional[Path], 
    dry_run: bool, 
    verbose: bool, 
    force: bool,
    source_dir: Optional[Path],
    dest_dir: Optional[Path], 
    collection_name: Optional[str]
):
    """Organize and rename photo collections with consistent schema.

    NormPic reads photos from a source directory, extracts EXIF metadata,
    generates standardized filenames based on timestamps, creates symlinks
    with consistent naming patterns, and produces JSON manifests.
    """
    try:
        # Build CLI overrides dictionary
        cli_overrides = {}
        if source_dir is not None:
            cli_overrides['source_dir'] = str(source_dir)
        if dest_dir is not None:
            cli_overrides['dest_dir'] = str(dest_dir) 
        if collection_name is not None:
            cli_overrides['collection_name'] = collection_name
        if force:
            cli_overrides['force_reprocess'] = True

        # Load configuration with full precedence system
        if config_path is None:
            config_path = Config.get_default_config_path()
            # Only use config file if it exists
            config_file = config_path if config_path.exists() else None
        else:
            config_file = config_path

        if verbose and config_file:
            click.echo(f"Loading configuration from: {config_file}")

        config = load_config_with_full_precedence(
            config_file=config_file,
            cli_overrides=cli_overrides
        )

        # Validate paths
        config.validate_paths()

        source_dir = Path(config.source_dir)
        dest_dir = Path(config.dest_dir)

        if verbose:
            click.echo(f"Source directory: {source_dir}")
            click.echo(f"Destination directory: {dest_dir}")
            click.echo(f"Collection: {config.collection_name}")
            if dry_run:
                click.echo("DRY RUN MODE - no symlinks will be created")

        # Process photos
        if verbose:
            click.echo("Processing photos...")

        manifest = organize_photos(
            source_dir=source_dir,
            dest_dir=dest_dir,
            collection_name=config.collection_name,
            collection_description=config.collection_description,
            dry_run=dry_run,
        )

        # Output summary
        pic_count = len(manifest.pics)
        warnings = 0  # TODO: Count warnings from manifest
        errors = 0  # TODO: Count errors from manifest

        click.echo(f"Processed {pic_count} pics, {warnings} warnings, {errors} errors")

        if verbose:
            manifest_file = "manifest.dryrun.json" if dry_run else "manifest.json"
            click.echo(f"Manifest written to: {dest_dir / manifest_file}")

    except FileNotFoundError as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"Configuration error: {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Unexpected error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
