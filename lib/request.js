// lib/fetcher.js
export default async function fetcher(endpoint, options = {}) {
  const url = `${process.env.NEXT_PUBLIC_API_DOMAIN}${endpoint}`;

  const config = {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  };

  const response = await fetch(url, config);
  if (!response.ok) {
    throw new Error(`Error: ${response.status}`);
  }
  return response.json();
}
