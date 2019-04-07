import { Component, OnInit } from '@angular/core';
import { RestService } from '../rest.service';

@Component({
  selector: 'app-awards',
  templateUrl: './awards.component.html',
  styleUrls: ['./awards.component.css']
})
export class AwardsComponent implements OnInit {

  users;
  global;
  topMsg;
  topImg;
  topEmj;
  topStk;
  topAvgSize;
  btmAvgSize;
  topAvgSentiment;
  btmAvgSentiment;
  topTg;
  topGodwin;
  displayedColumns = ['position', 'name', 'score'];

  constructor(private rest: RestService) { }

  getTop(data, prop, nb) {
  	return data.sort(function(a, b) { return a[prop] < b[prop] ? 1 : -1; }).slice(0, nb);
  }

  getBottom(data, prop, nb) {
  	return data.sort(function(a, b) { return a[prop] > b[prop] ? 1 : -1; }).slice(0, nb);
  }

  getGodwin(data, nb) {
  	return data.sort(
  		function(a, b) { 
  			return (a['words']['race'] + a['words']['hitler'] + a['words']['nazi']) 
  				< (b['words']['race'] + b['words']['hitler'] + b['words']['nazi']) ? 1 : -1; 
  		}
  	).slice(0, nb);
  }

  ngOnInit() {
	this.rest.getUsers()
    .subscribe(res => {
      this.users = res['users'];
      this.topMsg = this.getTop(this.users, 'ctnmsg', 3);
      console.log(this.topMsg);
      this.topImg = this.getTop(this.users, 'cntimg', 3);
  	  this.topEmj = this.getTop(this.users, 'cntemj', 3);
  	  this.topStk = this.getTop(this.users, 'cntStk', 3);
  	  this.topAvgSize = this.getTop(this.users, 'avgsize', 3);
  	  this.btmAvgSize = this.getBottom(this.users, 'avgsize', 3);
  	  this.topAvgSentiment = this.getTop(this.users, 'avgsentiment', 3);
  	  this.btmAvgSentiment = this.getBottom(this.users, 'avgsentiment', 3);
  	  this.topTg = this.getTop(this.users, 'words.tg', 3);
  	  this.topGodwin = this.getGodwin(this.users, 3);
    }, err => {
      console.log(err);
    });
  }

}
