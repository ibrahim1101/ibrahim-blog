import { getCollection } from 'astro:content';
export const categories = {ai:'AI & Technology',cyber:'Cybersecurity',gaming:'Gaming & Hardware',dev:'Developer & Open Source'} as const;
export const allArticles = async () => (await getCollection('articles')).sort((a,b)=>b.data.published.getTime()-a.data.published.getTime());
export const fmt = (d: Date) => new Intl.DateTimeFormat('en-IN',{day:'numeric',month:'short',year:'numeric',timeZone:'Asia/Kolkata'}).format(d);
