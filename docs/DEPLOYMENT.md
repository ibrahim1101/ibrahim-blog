# Deployment

Create the intended GitHub repository and protect its production branch before adding content. Do not upload the original ZIP wholesale without inspecting it: local drafts, evidence, history, backups and secrets must remain private. `.gitignore` excludes those directories for new files, but already tracked files remain tracked until explicitly removed from the Git index.

For Cloudflare Pages connect the repository, select the protected production branch, set root directory `website`, build command `npm run build`, and output directory `dist`. Use Node 24 or later. Only connect the new project; leave existing sites and unrelated DNS records unchanged. Add the new custom domain `blog.ibrahimshaik.com` using the Pages custom-domain workflow. Verify TLS, DNS and that only the protected branch deploys to production. Disable public PR preview deployments or protect them if drafts are sensitive.

## Contact form

The form intentionally displays the public email fallback until configured. To enable delivery, create a Cloudflare Turnstile widget for the intended host and supply `PUBLIC_TURNSTILE_SITE_KEY` at Pages build time and `TURNSTILE_SECRET` at runtime. Configure `CONTACT_WEBHOOK_URL` and `CONTACT_WEBHOOK_TOKEN` as runtime secrets. The HTTPS webhook must be a service you control that accepts a JSON POST `{name,email,message}` with `Authorization: Bearer <token>` and returns a 2xx response only once the message is accepted for delivery. The project does not provide that delivery service, and a webhook alone is not proof that email arrived. Set up and verify a real delivery service before advertising the form as operational. The function validates input, origin and Turnstile; apply Cloudflare rate limiting or an equivalent policy separately. Keep secrets out of Git and test real delivery from the deployed domain.

Pages Functions are in `website/functions/`; ensure your Pages deployment includes them. Confirm the static build, DNS, headers, contact delivery, and branch permissions after deployment. Nothing in this package has created Cloudflare resources or published a real article.
