export interface Config {
  aws: {
    region: string;
  };
  discord: {
    apiBaseUrl: string;
    token: string;
    clientId: string;
    clientSecret: string;
    publicKey: string;
  };
}
