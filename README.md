# action-manage-pr

Action for managing Pull Request

This action read through each pull request and add information in the comment about patch submission via Linux Bluetooth mailing list.

## Inputs

### target_repo

***Required*** Target repo to manage.

### action_token

***Required*** Access token for accessing/modifying the `target_repo`.

## Example workflow

```
name: Manage PR

on:
  schedule:
    - cron: "0 1 * * *"

jobs:
  manage_pr:

    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - name: Manage PR
      uses: bluez/action-manage-pr@master
      with:
        target_repo: bluez/bluez
        action_token: ${{ secrets.ACTION_TOKEN }}
```
