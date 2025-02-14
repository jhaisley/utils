# Utilities

This repository contains various utility programs, which may not justify having their own repo, might still be useful to someone else.

## Utilities

### docker_ip_list.py

This script lists Docker containers and their IP addresses. It can also append the information to a Pi-hole custom list.

#### Usage

```bash
python docker_ip_list.py [--pihole PIHOLE_CONTAINER_NAME] [--output-dir OUTPUT_DIR]
```

- `--pihole`: Name of the Pi-hole container to append to custom.list (optional).
- `--output-dir`: Directory to save the custom.list files (default: `/tmp`).

#### Example

```bash
python docker_ip_list.py --pihole pihole_container --output-dir /path/to/output
```

## Contributing

Feel free to submit issues or pull requests if you have any improvements or bug fixes.

## License

This project is licensed under the MIT License.
