import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import axios, { AxiosInstance } from 'axios';

type Params = Record<string, string | number>;
type Data = Record<string, any>;

@Injectable()
export class AxiosService {
  private instance: AxiosInstance;

  constructor(private readonly configService: ConfigService) {
    this.instance = axios.create({
      baseURL: this.configService.get<string>('discord.apiBaseUrl'),
      timeout: 5000,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json',
      },
    });
  }

  get<T = any>(endPoint: string, headers = {}) {
    return this.instance<T>({
      method: 'GET',
      url: endPoint,
      headers,
    });
  }

  getByParams<T = any>(endPoint: string, params: Params, headers = {}) {
    return this.instance<T>({
      method: 'GET',
      url: endPoint,
      params: params,
      headers,
    });
  }

  post<T = any>(endPoint: string, data: Data, headers = {}) {
    return this.instance<T>({
      method: 'POST',
      url: endPoint,
      data,
      headers,
    });
  }

  postFormUnlencoded<T = any>(endPoint: string, data: Data, headers = {}) {
    return this.instance<T>({
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
