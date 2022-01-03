import os

def nornir_set_creds(nr, username=None, password=None):
    """
    Handler so credentials are not stored in cleartext. Scripts by Kirt Byers.
    """
    if not username:
        username = os.environ.get("NORNIR_USER")
    if not password:
        password = os.environ.get("NORNIR_SECRET")

    for host in nr.inventory.hosts.values():
        host.username = username
        host.password = password