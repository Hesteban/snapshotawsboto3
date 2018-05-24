import boto3
import click

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

@click.command()
@click.option('--project', default=None,
               help="Only instaces for project (tag Project:<nam>)")
def list_instances(project):
    "List EC2 Instances"
    instances =[]
    if project is not None:
        filters = [{'Name': 'tag:Project', 'Values': [project]}]
        instances = ec2.instances.filter(Filters=filters)
    else:
        instances = ec2.instances.all()

    for i in instances:
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name)))

    return

if __name__ == '__main__':

    list_instances()




