export type TokenObject = {
  id?: number;
  username?: string;
  token: string;
  tenant?: string;
  app?: string;
  consumed?: number;
  consumed_on?: string;
  user?: UserObject
};


export type UserObject = {
  key: any;
  id?: number;
  label?: string;
  value?: number | string;
  name?: string;
};