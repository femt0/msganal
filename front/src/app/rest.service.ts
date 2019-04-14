import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';

const apiUrl = 'http://localhost:5000/' ;

@Injectable({
  providedIn: 'root'
})

export class RestService {
  constructor(private http: HttpClient) { }

  getGlobal() {
    return this.http.get(apiUrl + 'global');
  }

  getUsers() {
    return this.http.get(apiUrl + 'users');
  }

  getStickers() {
    return this.http.get(apiUrl + 'stickers');
  }

  postScan() {
    return this.http.post(apiUrl + 'fullscan', null);
  }

  postStart() {
    return this.http.post(apiUrl + 'start', null);
  }

  postStop() {
    return this.http.post(apiUrl + 'stop', null);
  }
}
