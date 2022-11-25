import { Component, Input } from '@angular/core';
import { NbDialogRef } from '@nebular/theme';

@Component({
  template: `
    <nb-card class="confirmation-window">
      <nb-card-header>
      {{ dialogHeader }}
      <button nbButton class="headerButton" size="xsmall" (click)="closeDialogNo()">X</button>
      </nb-card-header>
      <nb-card-body>
        {{ dialogMessage }}
      </nb-card-body>
      <nb-card-footer>
        <div class="footerButtonWrapper">
          <button nbButton size="small" status="info" (click)="closeDialogYes()">Yes</button>
          <button nbButton size="small" status="info" (click)="closeDialogNo()">No</button>
        </div>
      </nb-card-footer>
    </nb-card>
  `,
  styleUrls: ['./confirmationWindow.scss'],
})
export class ConfirmationWindow {

  @Input() dialogHeader: string = "Confirmation";
  @Input() dialogMessage: string = "";

  constructor(protected ref: NbDialogRef<ConfirmationWindow>) {
  }

  closeDialogYes() {
    this.ref.close(true);
  }

  closeDialogNo() {
    this.ref.close(false);
  }
}
