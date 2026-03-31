import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

export function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div>
        <h2>{{ServiceName}} Microfrontend</h2>
        {/* Module content here */}
      </div>
    </QueryClientProvider>
  );
}

export default App;
