(function () {
  'use strict';

  var CONTACT_EMAIL = 'info@tirobotix.com';
  var root = document.documentElement;
  var header = document.querySelector('.site-header');
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('nav');

  // Header background once the page is scrolled
  function onScroll() {
    header.classList.toggle('is-scrolled', window.scrollY > 12);
  }
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  // Mobile navigation
  function setNav(open) {
    root.classList.toggle('nav-open', open);
    toggle.setAttribute('aria-expanded', String(open));
    toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
  }
  toggle.addEventListener('click', function () {
    setNav(!root.classList.contains('nav-open'));
  });
  nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) setNav(false);
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setNav(false);
  });
  window.addEventListener('resize', function () {
    if (window.innerWidth > 900) setNav(false);
  });

  // Reveal-on-scroll and active nav link
  if ('IntersectionObserver' in window) {
    var revealer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          revealer.unobserve(entry.target);
        }
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.08 });

    document.querySelectorAll('.reveal').forEach(function (el, i) {
      // Stagger siblings inside grids slightly
      var siblings = el.parentElement.querySelectorAll(':scope > .reveal');
      var index = Array.prototype.indexOf.call(siblings, el);
      el.style.transitionDelay = Math.min(index, 3) * 80 + 'ms';
      revealer.observe(el);
    });

    var links = {};
    nav.querySelectorAll('a[href^="#"]:not(.btn)').forEach(function (a) {
      links[a.getAttribute('href').slice(1)] = a;
    });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        var link = links[entry.target.id];
        if (link) link.classList.toggle('is-active', entry.isIntersecting);
      });
    }, { rootMargin: '-45% 0px -50% 0px' });
    Object.keys(links).forEach(function (id) {
      var section = document.getElementById(id);
      if (section) spy.observe(section);
    });
  } else {
    document.querySelectorAll('.reveal').forEach(function (el) {
      el.classList.add('is-visible');
    });
  }

  // Contact form: compose an email to the association in the visitor's mail app
  var form = document.getElementById('contact-form');
  var note = document.getElementById('form-note');
  var defaultNote = note.textContent;

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var data = new FormData(form);
    var name = String(data.get('name') || '').trim();
    var email = String(data.get('email') || '').trim();
    var topic = String(data.get('topic') || '').trim();
    var message = String(data.get('message') || '').trim();

    var invalid = [];
    if (!name) invalid.push(form.elements.name);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) invalid.push(form.elements.email);
    if (!message) invalid.push(form.elements.message);

    Array.prototype.forEach.call(form.elements, function (el) {
      el.classList.remove('is-invalid');
    });
    if (invalid.length) {
      invalid.forEach(function (el) { el.classList.add('is-invalid'); });
      invalid[0].focus();
      note.textContent = 'Please fill in your name, a valid email address and a message.';
      note.classList.add('is-error');
      return;
    }

    note.textContent = defaultNote;
    note.classList.remove('is-error');

    var subject = '[TiRobotix] ' + topic + ' — ' + name;
    var body = message + '\n\n—\n' + name + '\n' + email;
    window.location.href = 'mailto:' + CONTACT_EMAIL +
      '?subject=' + encodeURIComponent(subject) +
      '&body=' + encodeURIComponent(body);
  });

  // Footer year
  var year = document.getElementById('year');
  if (year) year.textContent = new Date().getFullYear();
})();
