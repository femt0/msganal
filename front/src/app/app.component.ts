import { Component } from '@angular/core';
import { RestService } from './rest.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  
  globaluser;
  title;

  constructor(private rest: RestService) { }

  ngOnInit() {
	this.rest.getGlobal()
    .subscribe(res => {
      this.globaluser = res['user']
      console.log(this.globaluser)
      this.title = this.globaluser.name
    }, err => {
      console.log(err);
    });
  }
}
