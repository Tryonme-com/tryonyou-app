import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import NotFound from "@/pages/NotFound";
import { Route, Switch } from "wouter";
import ErrorBoundary from "./components/ErrorBoundary";
import { ThemeProvider } from "./contexts/ThemeContext";
import Home from "./pages/Home";
import TryOn from "./pages/TryOn";
import Catalogue from "./pages/Catalogue";
import FootScan from "./pages/FootScan";
import Investors from "./pages/Investors";
import Offre from "./pages/Offre";
import Manifeste from "./pages/Manifeste";

function Router() {
  return (
    <Switch>
      <Route path={"/"} component={Home} />
      <Route path={"/tryon"} component={TryOn} />
      <Route path={"/catalogue"} component={Catalogue} />
      <Route path={"/footscan"} component={FootScan} />
      <Route path={"/investors"} component={Investors} />
      <Route path={"/offre"} component={Offre} />
      <Route path={"/offer"} component={Offre} />
      <Route path={"/manifeste"} component={Manifeste} />
      <Route path={"/manifesto"} component={Manifeste} />
      <Route path={"/404"} component={NotFound} />
      <Route component={NotFound} />
    </Switch>
  );
}

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider defaultTheme="dark">
        <TooltipProvider>
          <Toaster
            position="bottom-center"
            theme="dark"
            toastOptions={{
              style: {
                background: "#1A1614",
                color: "#F5EFE0",
                border: "1px solid rgba(201, 168, 76, 0.4)",
                fontFamily: "Inter, sans-serif",
                fontSize: "13px",
                letterSpacing: "0.04em",
              },
            }}
          />
          <Router />
        </TooltipProvider>
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;
