import axios from 'axios';
import { Cookies } from 'react-cookie';

import {
  AxiosInterceptorReqConfig,
  AuthReqConfig,
  ReqRejected,
  AxiosInterceptorRes,
  AxiosRes,
  EndPoint,
  Params,
  DataForm,
  AccessToken,
} from './types';

export * from './types';

export class Axios {
  #instance;
  #auth;
  #cookie;
  #accessToekn;

  constructor(isAuthReq = false, baseURL = '', accessToekn: AccessToken) {
    this.#instance = axios.create({
      baseURL: `${baseURL}`,
    });
    this.#auth = isAuthReq;
    this.#cookie = new Cookies();
    this.#setInterceptor();
    this.#accessToekn = accessToekn;
  }

  /* Interceptor */
  #setInterceptor() {
    this.#instance.interceptors.request.use(
      this.#reqMiddleWare.bind(this),
      this.#reqOnError.bind(this)
    );
    this.#instance.interceptors.response.use(
      this.#resMiddleWare.bind(this),
      this.#resOnError.bind(this)
    );
  }

  /* Req */
  #reqMiddleWare(config: AxiosInterceptorReqConfig) {
    let newConfig = config;
    if (this.#auth) newConfig = this.#setAuthReq(newConfig);

    return newConfig;
  }

  #setAuthReq(config: AxiosInterceptorReqConfig): AuthReqConfig {
    const { headers } = config;
    const newConfig = {
      ...config,
      headers: {
        ...headers,
        Authorization: `Bearer ${this.#cookie.get(this.#accessToekn.key)}`,
      },
    };

    return newConfig;
  }

  #reqOnError(error: ReqRejected) {
    return Promise.reject(error);
  }

  /* Res */
  #resMiddleWare(res: AxiosInterceptorRes) {
    const { authorization } = res.headers;

    if (authorization) {
      this.#cookie.set(this.#accessToekn.key, authorization, {
        path: '/',
      });
    }

    return res;
  }

  #resOnError(error: AxiosRes) {
    return Promise.reject(error);
  }

  get<T = any>(endPoint: EndPoint) {
    return this.#instance<T>({
      method: 'GET',
      url: endPoint,
    });
  }

  getByParams<T = any>(endPoint: EndPoint, params: Params) {
    return this.#instance<T>({
      method: 'GET',
      url: `${endPoint}`,
      params: params,
    });
  }

  getByParmsAsBlob(endPoint: EndPoint, params: Params) {
    return this.#instance({
      method: 'GET',
      url: `${endPoint}`,
      params: params,
      responseType: 'blob',
    });
  }

  post(endPoint: EndPoint, data: DataForm) {
    return this.#instance({
      method: 'POST',
      url: `${endPoint}`,
      data,
    });
  }

  postMultipartFormData(endPoint: EndPoint, data: FormData, headers = {}) {
    return this.#instance({
      method: 'POST',
      url: `${endPoint}`,
      headers: {
        'Content-Type': 'multipart/form-data',
        ...headers,
      },
      data,
    });
  }

  postFormUnlencoded(endPoint: EndPoint, data: DataForm) {
    return this.#instance({
      method: 'POST',
      url: `${endPoint}`,
      headers: {
        accept: 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      data,
    });
  }

  put(endPoint: EndPoint, data: object) {
    return this.#instance({
      method: 'PUT',
      url: endPoint,
      data,
    });
  }

  patch(endPoint: EndPoint, data: object = {}) {
    return this.#instance({
      method: 'PATCH',
      url: endPoint,
      data,
    });
  }

  putFormData(endPoint: EndPoint, data: DataForm) {
    return this.#instance({
      method: 'PUT',
      url: `${endPoint}`,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      data,
    });
  }

  delete(endPoint: EndPoint, data: DataForm) {
    return this.#instance({
      method: 'DELETE',
      url: `${endPoint}`,
      data,
    });
  }
}
