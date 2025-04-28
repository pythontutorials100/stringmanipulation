// app/page.js

// Function to fetch data from Strapi
async function getStrapiData(path) {
  const baseUrl = process.env.NEXT_PUBLIC_STRAPI_API_URL;
  const url = new URL(path, baseUrl);

  console.log(`Fetching data from: ${url}`); // Log the URL being fetched

  try {
    const response = await fetch(url.toString());
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    // Strapi typically wraps content in a 'data' object, then 'attributes'
    return data.data?.attributes;
  } catch (error) {
    console.error("Could not fetch Strapi data:", error);
    return null; // Return null or handle error appropriately
  }
}

// The Page component is now async to fetch data before rendering
export default async function Home() {
  // Fetch the greeting message from Strapi
  const greetingData = await getStrapiData('/homepage-greeting');

  // Get the message text, provide a default if fetch fails
  const message = greetingData?.message || 'Could not load message from Strapi.';

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24 bg-gray-100">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-blue-700 mb-4">
          My Strapi + Next.js Site
        </h1>
        <p className="text-xl text-gray-800 p-6 bg-white rounded-lg shadow-md border border-blue-200">
          {/* Display the message fetched from Strapi here! */}
          {message}
        </p>
      </div>
    </main>
  );
}
