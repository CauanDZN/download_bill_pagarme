module.exports = {
  apps: [
    {
      name: "app",
      script: "./venv/bin/hypercorn",
      args: "app:app --bind 0.0.0.0:5000",
      interpreter: "none",
      cwd: "/home/cauan/download_bill_pagarme",
      env: {
        PATH: "/home/cauan/download_bill_pagarme/venv/bin:$PATH",
        HYPERCORN_FORWARD_ALLOW_IPS: "*"
      }
    }
  ]
}
