import { Buffer } from 'buffer';

export const getDocsMarkdown = async (
  owner: string,
  repo: string,
  path: string
) => {
  const url = `https://api.github.com/repos/${owner}/${repo}/contents/${path}`;

  const res = await fetch(url);
  const json = await res.json();

  console.log(window.Buffer);
  return Buffer.from(json.content, 'base64').toString('utf-8');
};
