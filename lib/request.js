// lib/fetcher.js
export default async function fetcher(endpoint, data) {
  const url = `${process.env.NEXT_PUBLIC_API_DOMAIN}${endpoint}`;

  const config = {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  };

  const response = await fetch(url, config);
  if (!response.ok) {
    throw new Error(`Error: ${response.status}`);
  }
  return response.json();
}
