import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from '@/components/ui/toaster';
import { TooltipProvider } from '@/components/ui/tooltip';
import NotFound from '@/pages/not-found';
import { Route, Switch, Router as WouterRouter } from 'wouter';
import { Shell } from '@/components/layout/Shell';

import Dashboard from '@/pages/Dashboard';
import Games from '@/pages/Games';
import GameDetail from '@/pages/GameDetail';
import Experiments from '@/pages/Experiments';
import NewExperiment from '@/pages/NewExperiment';
import ExperimentDetail from '@/pages/ExperimentDetail';
import Claims from '@/pages/Claims';
import Papers from '@/pages/Papers';
import PaperDetail from '@/pages/PaperDetail';

const queryClient = new QueryClient();

function Router() {
  return (
    <Shell>
      <Switch>
        <Route path="/" component={Dashboard} />
        <Route path="/games" component={Games} />
        <Route path="/games/:id" component={GameDetail} />
        <Route path="/experiments" component={Experiments} />
        <Route path="/experiments/new" component={NewExperiment} />
        <Route path="/experiments/:id" component={ExperimentDetail} />
        <Route path="/claims" component={Claims} />
        <Route path="/papers" component={Papers} />
        <Route path="/papers/:id" component={PaperDetail} />
        <Route component={NotFound} />
      </Switch>
    </Shell>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <WouterRouter base={import.meta.env.BASE_URL.replace(/\/$/, '')}>
          <Router />
        </WouterRouter>
        <Toaster />
      </TooltipProvider>
    </QueryClientProvider>
  );
}

export default App;
