import { Component, ViewContainerRef, ElementRef, ViewEncapsulation, Renderer2, Inject } from '@angular/core';
import { PipeTransform, Pipe } from '@angular/core';
import { Router } from '@angular/router';
import { DomSanitizer } from '@angular/platform-browser';

import { GUIGlobal } from './providers/GUIGlobal';
import { DOCUMENT } from '@angular/common';
import { OOTR_THEME, ThemeSwitcher } from './providers/theme-switcher.service';

@Pipe({ name: 'bypassSecurity' })
export class BypassSecurityPipe implements PipeTransform {
  constructor(private sanitizer: DomSanitizer) { }

  transform(url) {
    return this.sanitizer.bypassSecurityTrustResourceUrl(url);
  }
}

@Component({
  // keep ngx-app as name for websites backwards compatibility
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'ngx-app',
  template: `
      <div id="generator" class="${OOTR_THEME.DEFAULT}">
        <router-outlet></router-outlet>
      </div>
  `,
  // Shadow-DOM requires code tweaks within Nebular.
  // Style interference with website is addressed by usage of selector specificity.
  encapsulation: ViewEncapsulation.None
})
export class AppComponent {
  private changes: MutationObserver;

  constructor(public viewContainerRef: ViewContainerRef,
              private elm: ElementRef,
              private router: Router,
              private global: GUIGlobal,
              private readonly renderer: Renderer2,
              @Inject(DOCUMENT) private readonly document: Document,
              private readonly themeSwitcher: ThemeSwitcher,
  ) {
    global.globalInit(elm.nativeElement.id);
    this.observeInitialization();

    //Route manually at the start to avoid URL changes in the browser
    this.router.navigate(['/pages/generator'], { skipLocationChange: true });
  }

  private observeInitialization(): void {
    const outerBody = this.document.getElementsByTagName('body')[0];

    this.changes = new MutationObserver((mutations: MutationRecord[]) => {
      mutations.forEach((mutation: MutationRecord) => {
        if (this.isInitializationDone(mutation, outerBody)) {
          this.themeSwitcher.initTheme();
        }
      });
    });

    this.changes.observe(outerBody, {
      attributeFilter: ['class'],
    });
  }

  private isInitializationDone(mutation: MutationRecord, outerBody: HTMLBodyElement) {
    return mutation.attributeName === 'class' && outerBody.classList.contains('pace-done');
  }
}
