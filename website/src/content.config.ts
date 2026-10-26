import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';
const articles = defineCollection({loader:glob({pattern:'**/*.md',base:'./src/content/articles'}),schema:z.object({title:z.string().min(1),description:z.string().min(1),category:z.enum(['ai','cyber','gaming','dev']),author:z.string().default('Shaik Ibrahim'),published:z.coerce.date(),updated:z.coerce.date().optional(),sources:z.array(z.object({title:z.string(),url:z.string().url()})).min(1),disclosure:z.string().min(1)})});
export const collections = { articles };
