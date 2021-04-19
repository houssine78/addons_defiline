(function() {
  'use strict';
  
  var MATERIAL_COUNT = 30;
  var CUBE_SIZE = 300;
  var CUBE_INCREMENT = 100;
  var SPREAD = 1000;

  var materials;
  var scene;
  var renderer;
  var camera;
  var stats;
  var cubes = [];
  var materials = [];
  var cubeHolder;
  var rotSpeed;
  var cubeCount = 0;
  var geometry;
  var windowHalfX;
  var windowHalfY;
  var mouseX = 0;
  var mouseY = 0;
  

  var website = openerp.website;
  website.openerp_website = {};
  website.snippet.animationRegistry.banner_webgl = website.snippet.Animation.extend({
    selector : ".particle_banner",
    start : function() {

      this.initBanner();
    },

    initBanner : function() {
      var self = this;
      // stop the user getting a text cursor
      document.onselectstart = function() {
        return false;
      };
      // init 3D world
       var container = document.createElement('div');
      this.$target.find(".particle_banner_container").empty();
      this.$target.find(".particle_banner_container").append(this.container)
      renderer = new THREE.WebGLRenderer({
        antialias : false,
        alpha : true,
      });
      container.appendChild(renderer.domElement);
      camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 20, 3000);
      camera.position.z = 1000;
      scene = new THREE.Scene();
      scene.add(camera);
      // init object to hold cubes and rotate
      cubeHolder = new THREE.Object3D();
      scene.add(cubeHolder);

      // add lights
      var light = new THREE.PointLight(0xffeeaa, 1);
      light.position = new THREE.Vector3(-1000, 1000, -1000);
      scene.add(light);

      var light2 = new THREE.PointLight(0xFFFFFF, 1);
      light2.position = new THREE.Vector3(1000, 1000, 1000);
      scene.add(light2);

      // init materials
      for (var i = 0; i < this.MATERIAL_COUNT; i++) {
        var material = new THREE.MeshLambertMaterial({
          opacity : 0.5,
          blending : THREE.AdditiveBlending,
          depthTest : false,
          transparent : true
        });
        material.color = new THREE.Color(0x555555);
        materials.push(material)
      }

      // init cubes
      this.geometry = new THREE.CubeGeometry(self.CUBE_SIZE, self.CUBE_SIZE, self.CUBE_SIZE);
      this.addCubes();

      // match speed with Stage3D version in degrees
      this.rotSpeed = .3 / 360 * Math.PI * 2;

      $(window).resize({
        'self' : self
      }, self.onWindowResize);

      $(window).on('mousemove', {
        'self' : self
      }, self.onMouseMove);

      $(window).trigger('resize');
      this.animate();
    },

    addCubes : function() {
      var self = this;
      cubeCount += CUBE_INCREMENT;

      // init cubes
      for (var j = 0; j < CUBE_INCREMENT; j++) {
        var cube = new THREE.Mesh(geometry, materials[j % MATERIAL_COUNT]);
        // randomize size
        cube.scale.x = cube.scale.y = cube.scale.z = Math.random() + .1;

        cubeHolder.add(cube);
        cubes.push(cube);

        cube.position.x = Math.random() * SPREAD - SPREAD / 2;
        cube.position.y = Math.random() * SPREAD - SPREAD / 2;
        cube.position.z = Math.random() * SPREAD - SPREAD / 2;

        cube.rotation.x = Math.random() * 2 * Math.PI - Math.PI;
        cube.rotation.y = Math.random() * 2 * Math.PI - Math.PI;
        cube.rotation.z = Math.random() * 2 * Math.PI - Math.PI;
      }

      // make more cubes less opaque
      for (var i = 0; i < MATERIAL_COUNT; i++) {
        
        materials[i].opacity = 50 / cubeCount;
      }
    },

    onMouseMove : function(event) {
      var self = event.data.self;
      mouseX = event.clientX - windowHalfX;
      mouseY = event.clientY - windowHalfY;
    },

    onWindowResize : function(event) {
      if (event) {
        var self = event.data.self;
        windowHalfX = window.innerWidth / 2;
        windowHalfY = window.innerHeight / 2;
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
      }
    },

    animate : function() {
      var self = this;
      setInterval(function() {
        self.render();
      }, 1000 / 60);
    },

    render : function() {
      var self = this;
      camera.position.x += (mouseX - camera.position.x) * 0.1;
      camera.position.y += (-mouseY - camera.position.y) * 0.1;
      // always look at center
      camera.lookAt(cubeHolder.position);

      cubeHolder.rotation.y -= rotSpeed;
      for (var i = 0; i < self.cubeCount; i++) {
        self.cubes[i].rotation.x += rotSpeed;
      }
      renderer.render(scene, camera);
    }

  });
})();
