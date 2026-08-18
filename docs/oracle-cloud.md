# Deploy odpt to Oracle Cloud (free, 24/7)

District.in blocks GitHub Actions and most US/EU datacenter IPs. A **free Oracle Cloud VM in Mumbai** uses an Indian IP that works — and stays on without your laptop.

## 1. Create Oracle Cloud account

1. Go to [cloud.oracle.com/free](https://www.oracle.com/cloud/free/)
2. Sign up (card required for verification, Always Free tier won't charge)
3. Choose **Home region: India West (Mumbai)** — or Hyderabad/Singapore if Mumbai is out of capacity

## 2. Create a free VM

1. **Compute → Instances → Create instance**
2. Name: `odpt`
3. Image: **Ubuntu 24.04** (aarch64 if using ARM)
4. Shape: **VM.Standard.A1.Flex** (Always Free) — 1 OCPU, 6 GB RAM is enough
5. Networking: use default VCN; ensure **Assign public IPv4**
6. SSH keys: paste your public key (`~/.ssh/id_ed25519.pub` or generate with `ssh-keygen`)
7. Create

If you see "Out of host capacity", retry off-peak or try **Hyderabad** as home region.

## 3. Open SSH in firewall

1. **Networking → Virtual cloud networks → your VCN → Security Lists → Default**
2. Ingress rule: Source `0.0.0.0/0`, Protocol TCP, Port **22**

## 4. Install odpt on the VM

```bash
ssh ubuntu@YOUR_VM_PUBLIC_IP

# One-liner (replace with your bot token):
curl -fsSL https://raw.githubusercontent.com/architv/odpt/main/scripts/setup-oracle-vm.sh | sudo bash -s -- YOUR_TELEGRAM_BOT_TOKEN
```

That's it. The VM checks every 10 minutes, skips 2–8 AM IST, and sends Telegram alerts.

## Useful commands

```bash
sudo tail -f /opt/odpt/tracker.log
sudo systemctl status odpt.timer
sudo systemctl start odpt.service    # run check now
```

## Cost

**$0/month** on Oracle Always Free tier — runs forever, no laptop needed.
