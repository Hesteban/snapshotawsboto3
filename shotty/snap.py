import boto3
import click
import botocore

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []
    if project is not None:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    return instances

def has_pending_snapshots(volume):
    snapshots = list(volume.snapshots.all())
    return snapshots and snapshots[0].state == 'pending'


@click.group()
def cli():
    """Shotty manages snapshots"""

@cli.group('snapshots')
def snapshots():
    """Commands for snapshots"""

@snapshots.command('list')
@click.option('--project', default=None,
               help="Only snapshots within instances for project (tag Project:<nam>)")
def list_snapshots(project):
    "List EC2 Snapshots"

    instances = filter_instances(project)
    for i in instances:
        for v in i.volumes.all():
            for s in v.snapshots.all():
                print(",".join((
                    s.id,
                    v.id,
                    i.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c")
                )))

    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project', default=None,
               help="Only volumes within instances for project (tag Project:<nam>)")
def list_volumes(project):
    "List EC2 Volumes"

    instances = filter_instances(project)

    for i in instances:
        for v in i.volumes.all():
            print(",".join((
                v.id,
                i.id,
                v.state,
                str(v.size) + "GiB",
                v.encrypted and "Encrypted" or "Not Encrypted"
            )))


@cli.group('instances')
def instances():
    """Commands for instances"""
@instances.command('snapshots')
@click.option('--project', default=None,
               help="Only instaces for project (tag Project:<nam>)")
def create_snapshots(project):
    "Create snapshots for  EC2 Instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stoping instance {0}".format(i.id))
        i.stop()
        i.wait_until_stopped()
        for v in i.volumes.all():
            if has_pending_snapshots(v):
                print(" Skipping {0}, snapshot already in progress".format(v.id))
                continue
            print("Creating snapshot of {0}".format(v.id))
            v.create_snapshot(Description = "Snapshot created from shotty")
        print("Starting instance {0}".format(i.id))
        i.start()
        i.wait_until_running()
    return


@instances.command('list')
@click.option('--project', default=None,
               help="Only instaces for project (tag Project:<nam>)")
def list_instances(project):
    "List EC2 Instances"

    instances = filter_instances(project)

    for i in instances:
        dic_tags = {dic['Key']: dic['Value'] for dic in i.tags or []}
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name)),
            dic_tags.get('Project', '<No project>'))

    return

@instances.command('stop')
@click.option('--project', default=None,
               help="Only instaces for project (tag Project:<nam>)")
def stop_instaces(project):
    "Stop EC2 Instances"
    instances= filter_instances(project)

    for i in instances:
        print("Stopping {0}...".format(i.id))
        try:
            i.stop()
        except botocore.execeptions.ClientError as e:
            print("Could not stop the instance {0} - invalid state".format(i.id) + str(e))
            continue
    return

@instances.command('start')
@click.option('--project', default=None,
               help="Only instaces for project (tag Project:<nam>)")
def start_instaces(project):
    "Start EC2 Instances"
    instances= filter_instances(project)

    for i in instances:
        print("Starting {0}...".format(i.id))
        try:
            i.start()
        except botocore.execeptions.ClientError as e:
            print("Could not start the instance {0} - invalid state".format(i.id) + str(e))
            continue
    return


if __name__ == '__main__':
    cli()
