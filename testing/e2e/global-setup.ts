import { FullConfig } from '@playwright/test';

async function globalSetup(config: FullConfig) {
  console.log('🔧 E2E Global Setup');
  
  // Log the configuration that was set by the shell script
  const offlineMode = process.env.POWERIT_OFFLINE_E2E !== 'false';
  const backendOffline = process.env.POWERIT_OFFLINE;
  
  console.log(`⚙️  Environment Configuration:`);
  console.log(`   • POWERIT_OFFLINE: ${backendOffline || 'not set'}`);
  console.log(`   • POWERIT_OFFLINE_E2E: ${process.env.POWERIT_OFFLINE_E2E || 'not set (defaults to true)'}`);
  console.log(`   • Effective test mode: ${offlineMode ? 'OFFLINE' : 'ONLINE'}`);
  
  if (offlineMode) {
    console.log(`⚡ Tests configured for OFFLINE mode`);
    console.log(`   • Faster execution using mock responses`);
    console.log(`   • No external API calls`);
  } else {
    console.log(`🌐 Tests configured for ONLINE mode`);
    console.log(`   • Will make actual API calls`);
    console.log(`   • Requires valid API keys`);
  }
  
  console.log(`✅ Global setup completed\n`);
}

export default globalSetup; 