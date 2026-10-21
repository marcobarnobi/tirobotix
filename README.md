# tirobotix.com

Static website for **TiRobotix**, a robotics hobby and development association.
It is plain HTML, CSS and JavaScript with no build step, so any static host can serve it.

```
index.html              The page (all copy lives here)
css/styles.css          Styles (colors and fonts are set at the top in :root)
js/main.js              Mobile menu, scroll effects, contact form
favicon.svg             Browser tab icon
assets/img/             Illustrations (SVG) and the social share image (og-image.png)
tools/generate_art.py   Regenerates the three SVG illustrations
```

## Preview locally

```sh
python3 -m http.server 8000
# open http://localhost:8000
```

## Deploy

The site is hosted on **GitHub Pages** from the `main` branch of this repo. Every push to `main` publishes
automatically. `CNAME` sets the custom domain, and `.nojekyll` makes GitHub serve the files as they are.

DNS is managed at GoDaddy:

| Type  | Name  | Value                     |
|-------|-------|---------------------------|
| A     | @     | 185.199.108.153           |
| A     | @     | 185.199.109.153           |
| A     | @     | 185.199.110.153           |
| A     | @     | 185.199.111.153           |
| CNAME | www   | marcobarnobi.github.io    |

## Contact email

The site uses **info@tirobotix.com** in these places: the contact card, the footer, the "Join" links,
the JSON-LD block in `index.html`, and `CONTACT_EMAIL` in `js/main.js`.

The contact form has no server. It opens the visitor's email app with a pre-filled message to that address.
To receive form submissions directly instead, point the form at a service such as Formspree or Netlify Forms.

Make sure the mailbox `info@tirobotix.com` exists (through your domain registrar, Google Workspace,
Zoho Mail, or Cloudflare Email Routing for forwarding) so that messages are delivered.

## Editing the illustrations

The urban, agricultural and blueprint illustrations are generated:

```sh
python3 tools/generate_art.py assets/img
```
