import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
export default defineConfig({site:'https://blog.ibrahimshaik.com',integrations:[sitemap()]});
