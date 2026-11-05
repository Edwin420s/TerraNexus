import React, { useState } from 'react';
import { Layout } from './components/Layout';
import { DashboardView } from './views/DashboardView';
import { IrrigationControlView } from './views/IrrigationControlView';
import { IntelligenceWorkspaceView } from './views/IntelligenceWorkspaceView';
import { FarmsAndFieldsView } from './views/FarmsAndFieldsView';
import { DevicesAndTelemetryView } from './views/DevicesAndTelemetryView';
import { OperationsView } from './views/OperationsView';
import { AlertsAndMonitoringView } from './views/AlertsAndMonitoringView';
import { PlatformDirectoryView } from './views/PlatformDirectoryView';

export const App: React.FC = () => {
  const [currentRoute, setCurrentRoute] = useState<string>('/dashboard');

  const renderCurrentView = () => {
    switch (currentRoute) {
      case '/fields':
      case '/farms':
        return <FarmsAndFieldsView />;
      case '/irrigation/control':
      case '/irrigation':
        return <IrrigationControlView />;
      case '/intelligence':
      case '/recommendations':
        return <IntelligenceWorkspaceView />;
      case '/devices':
      case '/sensors':
      case '/telemetry':
        return <DevicesAndTelemetryView />;
      case '/operations':
      case '/tasks':
        return <OperationsView />;
      case '/alerts':
      case '/monitoring':
        return <AlertsAndMonitoringView />;
      case '/directory':
        return <PlatformDirectoryView onNavigate={(route) => setCurrentRoute(route)} />;
      case '/dashboard':
      default:
        return <DashboardView onNavigate={(route) => setCurrentRoute(route)} />;
    }
  };

  return (
    <Layout currentRoute={currentRoute} onNavigate={(route) => setCurrentRoute(route)}>
      {renderCurrentView()}
    </Layout>
  );
};
export default App;
