#!/usr/bin/env python3

import subprocess
import json
import argparse
import time

# Define epoch time at the start of the script
EPOCH_TIME = int(time.time())


def get_host_ip():
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, check=True)
        return result.stdout.split()[0]
    except subprocess.CalledProcessError:
        return 'N/A'


def get_container_ip(container_name):
    try:
        result = subprocess.run(
            ['docker', 'inspect', '--format', '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}', container_name],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def copy_pihole_custom_list(pihole_container_name, output_dir):
    try:
        bak_path = f'{output_dir}/{EPOCH_TIME}-custom.list.bak'
        new_path = f'{output_dir}/{EPOCH_TIME}-custom.list.new'
        subprocess.run(
            ['docker', 'cp', f'{pihole_container_name}:/etc/pihole/custom.list', bak_path],
            check=True
        )
        subprocess.run(['cp', bak_path, new_path], check=True)
        return new_path
    except subprocess.CalledProcessError as e:
        print(f'Error copying custom.list from Pi-hole container: {e}')
        exit(1)


def append_to_pihole_custom_list(container_name, ip, local_path):
    try:
        with open(local_path, 'a+') as f:
            f.seek(0)
            existing_entries = f.read().splitlines()
            new_entry = f'{ip} {container_name}'
            if new_entry not in existing_entries:
                f.write(f'{new_entry}\n')
    except Exception as e:
        print(f'Error writing to custom.list: {e}')
        exit(1)


def get_container_info(pihole_container_name=None, output_dir='/tmp'):
    try:
        result = subprocess.run(['docker', 'ps', '-q'], capture_output=True, text=True, check=True)
        container_ids = result.stdout.split()
        if not container_ids:
            print('No running containers found.')
            return

        local_path = None
        if pihole_container_name:
            local_path = copy_pihole_custom_list(pihole_container_name, output_dir)

        for cid in container_ids:
            container_name = subprocess.run(
                ['docker', 'inspect', '--format', '{{ .Name }}', cid],
                capture_output=True, text=True, check=True
            ).stdout.strip().lstrip('/ ')

            container_networks = subprocess.run(
                ['docker', 'inspect', '--format', '{{json .NetworkSettings.Networks}}', cid],
                capture_output=True, text=True, check=True
            ).stdout.strip()

            networks = json.loads(container_networks)
            ips = [net['IPAddress'] for net in networks.values() if net['IPAddress']]

            if not ips:
                network_mode = subprocess.run(
                    ['docker', 'inspect', '--format', '{{.HostConfig.NetworkMode}}', cid],
                    capture_output=True, text=True, check=True
                ).stdout.strip()
                if network_mode == 'host':
                    ips.append(get_host_ip())

            if not ips:
                ips.append('N/A')

            print(f'{container_name} {" ".join(ips)}')

            if pihole_container_name and local_path:
                append_to_pihole_custom_list(container_name, ips[0], local_path)

        if pihole_container_name and local_path:
            subprocess.run(
                ['docker', 'cp', local_path, f'{pihole_container_name}:/etc/pihole/custom.list'],
                check=True
            )

    except subprocess.CalledProcessError as e:
        print(f'Error: {e}')
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='List Docker containers and their IP addresses.')
    parser.add_argument('--pihole', type=str, help='Name of the Pi-hole container to append to custom.list')
    parser.add_argument('--output-dir', type=str, default='/tmp', help='Directory to save the custom.list files')
    args = parser.parse_args()
    get_container_info(args.pihole, args.output_dir)
