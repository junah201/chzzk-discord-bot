import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios, { AxiosInstance } from 'axios';

type Params = Record<string, string | number | boolean | null>;
type Data = Record<string, any>;
type InterfaceType = 'discord' | 'chzzk';

@Injectable()
export class AxiosService {
  private instances: Map<InterfaceType, AxiosInstance> = new Map();

  constructor(private readonly configService: ConfigService) {
    this.createInstance(
      'discord',
      this.configService.get<string>('discord.apiBaseUrl') as string,
    );
    this.createInstance(
      'chzzk',
      this.configService.get<string>('chzzk.apiBaseUrl') as string,
    );
  }

  private createInstance(name: InterfaceType, baseURL: string) {
    const instance = axios.create({
      baseURL,
      timeout: 5000,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    });

    instance.interceptors.response.use(
      (response) => response,
      (error) => {
        if (
          error.response &&
          error.response.status >= 400 &&
          error.response.status < 500
        ) {
          return Promise.resolve(error.response);
        }
        return Promise.reject(error);
      },
    );

    this.instances.set(name, instance);
  }

  get<T = any>(service: InterfaceType, endPoint: string, headers = {}) {
    return this.instances.get(service)!.request<T>({
      method: 'GET',
      url: endPoint,
      headers,
    });
  }

  getByParams<T = any>(
    service: InterfaceType,
    endPoint: string,
    params: Params,
    headers = {},
  ) {
    return this.instances.get(service)!.request<T>({
      method: 'GET',
      url: endPoint,
      params: params,
      headers,
    });
  }

  post<T = any>(
    service: InterfaceType,
    endPoint: string,
    data: Data,
    headers = {},
  ) {
    return this.instances.get(service)!.request<T>({
      method: 'POST',
      url: endPoint,
      data,
      headers,
    });
  }

  postFormUnlencoded<T = any>(
    service: InterfaceType,
    endPoint: string,
    data: Data,
    headers = {},
  ) {
    return this.instances.get(service)!.request<T>({
      method: 'POST',
      url: endPoint,
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        ...headers,
      },
      data,
    });
  }
}
