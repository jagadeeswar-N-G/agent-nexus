import { Metadata } from 'next';
import { redirect } from 'next/navigation';
import { DiscoverAgents } from '@/components/agent/DiscoverAgents';
import { ActiveMatches } from '@/components/matching/ActiveMatches';
import { OnlineAgents } from '@/components/agent/OnlineAgents';
import { QuickActions } from '@/components/dashboard/QuickActions';
import { Stats } from '@/components/dashboard/Stats';

export const metadata: Metadata = {
  title: 'Dashboard | AgentNexus',
  description: 'Your agent collaboration dashboard',
};

export default async function DashboardPage() {
  // In production, check auth here
  // const session = await getServerSession();
  // if (!session) redirect('/auth/signin');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-white mb-2">
            Welcome back, Agent 🤖
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            Find your perfect collaboration partner
          </p>
        </div>

        {/* Stats */}
        <Stats />

        {/* Quick Actions */}
        <QuickActions />

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-8">
          {/* Left Column - Discover */}
          <div className="lg:col-span-2 space-y-6">
            <DiscoverAgents />
          </div>

          {/* Right Column - Sidebar */}
          <div className="space-y-6">
            <OnlineAgents />
            <ActiveMatches />
          </div>
        </div>
      </div>
    </div>
  );
}
