// Clear Astro's content cache and previous output so removed articles cannot leak into a new build.
import {rmSync} from 'node:fs';
rmSync(new URL('../.astro',import.meta.url),{recursive:true,force:true});
rmSync(new URL('../dist',import.meta.url),{recursive:true,force:true});
rmSync(new URL('../node_modules/.astro',import.meta.url),{recursive:true,force:true});
