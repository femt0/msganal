import { Component } from '@angular/core';
import { RestService } from './rest.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  
  global;
  title;

  constructor(private rest: RestService) { }

  ngOnInit() {
	this.rest.getGlobal()
    .subscribe(res => {
      this.global = res['user']
      console.log(this.global)
      this.title = this.global.name
    }, err => {
      console.log(err);
    });
  }
}
