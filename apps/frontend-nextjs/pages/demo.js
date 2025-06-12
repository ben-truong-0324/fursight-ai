// apps/frontend-nextjs/pages/demo.js

// Basic inline styles to avoid external file dependencies.
const styles = {
    container: {
      padding: '0 2rem',
    },
    main: {
      minHeight: '100vh',
      padding: '4rem 0',
      flex: 1,
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
    },
    title: {
      margin: 0,
      lineHeight: 1.15,
      fontSize: '4rem',
      textAlign: 'center',
    },
    description: {
      textAlign: 'center',
      margin: '4rem 0',
      lineHeight: 1.5,
      fontSize: '1.5rem',
    },
    card: {
      margin: '1rem',
      padding: '1.5rem',
      textAlign: 'left',
      color: 'inherit',
      textDecoration: 'none',
      border: '1px solid #eaeaea',
      borderRadius: '10px',
      transition: 'color 0.15s ease, border-color 0.15s ease',
      maxWidth: '800px',
    },
  };
  
  // This is our React component. It receives the API data via props.
  export default function DemoPage({ apiResponse, error }) {
    return (
      <div style={styles.container}>
        <main style={styles.main}>
          <h1 style={styles.title}>
            API Integration Demo
          </h1>
  
          <p style={styles.description}>
            This page fetches data from the FastAPI backend on the server-side.
          </p>
  
          <div>
            <div style={styles.card}>
              <h2>Backend Says:</h2>
              {error ? (
                <p style={{ color: 'red' }}>{error}</p>
              ) : (
                <p><code>{JSON.stringify(apiResponse)}</code></p>
              )}
            </div>
          </div>
        </main>
      </div>
    );
  }
  
  // This function runs on the server for every request to this page.
  export async function getServerSideProps() {
    try {
      // This is the internal Kubernetes service URL
      const res = await fetch('http://backend-fastapi:8000/api');
      
      if (!res.ok) {
        throw new Error(`Failed to fetch: ${res.status} ${res.statusText}`);
      }
      
      const apiResponse = await res.json();
  
      // The fetched data is passed to the page component as props.
      return { props: { apiResponse } };
    } catch (e) {
      console.error("Failed to fetch from backend API:", e);
      // Pass error information to the page component.
      return { props: { error: e.message } };
    }
  }