# snapshotawsboto3
Demo project to manage AWS EC2 instance snapshots

## Configuring

shotty uses the configuration file created by:
`aws configure --profile shotty`

## Running
`python shotty\snap.py <command> <subcommand> <--project= PROJECT>""`

*command* is instances, volumes, or snapshots
*subcommand* - depends on command
*project* is optional
