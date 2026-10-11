import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'fr.jarvis.mobile',
  appName: 'JARVIS',
  webDir: 'native-app/www',
  ios: {
    contentInset: 'automatic'
  }
};

export default config;
