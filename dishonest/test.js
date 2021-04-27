function hash(_0x3c9b7c) {
  function _0x23b987(_0x1daa32, _0x2b7e42) {
    return (_0x1daa32 & 2147483647) + (_0x2b7e42 & 2147483647) ^ _0x1daa32 & 2147483648 ^ _0x2b7e42 & 2147483648;
  }

  function _0x4026be(_0x598a0f) {
    var _0x282ca1 = "0123456789abcdef";
    var _0xfad06e = "";

    for (var _0x29d201 = 7; _0x29d201 >= 0; _0x29d201--) {
      _0xfad06e += _0x282ca1["charAt"](_0x598a0f >> _0x29d201 * 4 & 15);
    }

    return _0xfad06e;
  }

  function _0x3d7921(_0xc52d0b) {
    var _0x2ad96a = (_0xc52d0b["length"] + 8 >> 6) + 1,
        _0x38a083 = new Array(_0x2ad96a * 16);

    for (var _0x185049 = 0; _0x185049 < _0x2ad96a * 16; _0x185049++) {
      _0x38a083[_0x185049] = 0;
    }

    for (_0x185049 = 0; _0x185049 < _0xc52d0b["length"]; _0x185049++) {
      _0x38a083[_0x185049 >> 2] |= _0xc52d0b["charCodeAt"](_0x185049) << 24 - (_0x185049 & 3) * 8;
    }

    _0x38a083[_0x185049 >> 2] |= 128 << 24 - (_0x185049 & 3) * 8;
    _0x38a083[_0x2ad96a * 16 - 1] = _0xc52d0b["length"] * 8;
    return _0x38a083;
  }

  function _0x38f6e0(_0x22c38c, _0x5b3b12) {
    return _0x22c38c << _0x5b3b12 | _0x22c38c >>> 32 - _0x5b3b12;
  }

  function _0x18c7ba(_0x35fa09, _0x145773, _0x3a234a, _0x33d62f) {
    if (_0x35fa09 < 20) {
      return _0x145773 & _0x3a234a | ~_0x145773 & _0x33d62f;
    }

    if (_0x35fa09 < 40) {
      return _0x145773 ^ _0x3a234a ^ _0x33d62f;
    }

    if (_0x35fa09 < 60) {
      return _0x145773 & _0x3a234a | _0x145773 & _0x33d62f | _0x3a234a & _0x33d62f;
    }

    return _0x145773 ^ _0x3a234a ^ _0x33d62f;
  }

  function _0x5255fb(_0x480121) {
    return _0x480121 < 20 ? 1518500249 : _0x480121 < 40 ? 1859775393 : _0x480121 < 60 ? -1894007588 : -899497514;
  }

  var _0x1694bf = _0x3d7921(_0x3c9b7c);

  var _0x496a09 = new Array(80);

  var _0x31b194 = 1732584193;

  var _0x2b956c = -271733879;

  var _0x48d9c9 = -1732584194;

  var _0x1e16da = 271733878;

  var _0x458cfa = -1009589776;

  for (var _0xf279de = 0; _0xf279de < _0x1694bf["length"]; _0xf279de += 16) {
    var _0x46473e = _0x31b194;
    var _0x3eca41 = _0x2b956c;
    var _0x5075e2 = _0x48d9c9;
    var _0x13f06d = _0x1e16da;
    var _0x54fd29 = _0x458cfa;

    for (var _0xbedea6 = 0; _0xbedea6 < 80; _0xbedea6++) {
      if (_0xbedea6 < 16) {
        _0x496a09[_0xbedea6] = _0x1694bf[_0xf279de + _0xbedea6];
      } else {
        _0x496a09[_0xbedea6] = _0x38f6e0(_0x496a09[_0xbedea6 - 3] ^ _0x496a09[_0xbedea6 - 8] ^ _0x496a09[_0xbedea6 - 14] ^ _0x496a09[_0xbedea6 - 16], 1);
      }

      t = _0x23b987(_0x23b987(_0x38f6e0(_0x31b194, 5), _0x18c7ba(_0xbedea6, _0x2b956c, _0x48d9c9, _0x1e16da)), _0x23b987(_0x23b987(_0x458cfa, _0x496a09[_0xbedea6]), _0x5255fb(_0xbedea6)));
      _0x458cfa = _0x1e16da;
      _0x1e16da = _0x48d9c9;
      _0x48d9c9 = _0x38f6e0(_0x2b956c, 30);
      _0x2b956c = _0x31b194;
      _0x31b194 = t;
    }

    _0x31b194 = _0x23b987(_0x31b194, _0x46473e);
    _0x2b956c = _0x23b987(_0x2b956c, _0x3eca41);
    _0x48d9c9 = _0x23b987(_0x48d9c9, _0x5075e2);
    _0x1e16da = _0x23b987(_0x1e16da, _0x13f06d);
    _0x458cfa = _0x23b987(_0x458cfa, _0x54fd29);
  }

  return _0x4026be(_0x31b194) + _0x4026be(_0x2b956c) + _0x4026be(_0x48d9c9) + _0x4026be(_0x1e16da) + _0x4026be(_0x458cfa);
}

function go(_0x2323c8) {
  function _0x51dceb() {
    var _0x15c8a7 = window["navigator"]["userAgent"],
        _0x3b05ff = ["Phantom"];

    for (var _0x239a65 = 0; _0x239a65 < _0x3b05ff["length"]; _0x239a65++) {
      if (_0x15c8a7["indexOf"](_0x3b05ff[_0x239a65]) != -1) {
        return true;
      }
    }

    if (window["callPhantom"] || window["_phantom"] || window["Headless"] || window["navigator"]["webdriver"] || window["navigator"]["__driver_evaluate"] || window["navigator"]["__webdriver_evaluate"]) {
      return true;
    }
  }

  if (_0x51dceb()) {
    return;
  }

  var _0x2c3917 = new Date();

  function _0x318358(_0x441b80, _0x49cbe2) {
    var _0x1be730 = _0x2323c8["chars"]["length"];

    for (var _0x84d4ad = 0; _0x84d4ad < _0x1be730; _0x84d4ad++) {
      for (var _0x3b0257 = 0; _0x3b0257 < _0x1be730; _0x3b0257++) {
        var _0x490d78 = _0x49cbe2[0] + _0x2323c8["chars"]["substr"](_0x84d4ad, 1) + _0x2323c8["chars"]["substr"](_0x3b0257, 1) + _0x49cbe2[1];

        if (hash(_0x490d78) == _0x441b80) {
          return [_0x490d78, new Date() - _0x2c3917];
        }
      }
    }
  }

  var _0x38f5ef = _0x318358(_0x2323c8["ct"], _0x2323c8["bts"]);

  if (_0x38f5ef) {
    var _0x182e5a;

    if (_0x2323c8["wt"]) {
      _0x182e5a = parseInt(_0x2323c8["wt"]) > _0x38f5ef[1] ? parseInt(_0x2323c8["wt"]) - _0x38f5ef[1] : 500;
    } else {
      _0x182e5a = 1500;
    }

    setTimeout(function () {
      document["cookie"] = _0x2323c8["tn"] + "=" + _0x38f5ef[0] + ";Max-age=" + _0x2323c8["vt"] + "; path = /";
      location["href"] = location["pathname"] + location["search"];
    }, 9999999);
  } else {
    alert("\u8BF7\u6C42\u9A8C\u8BC1\u5931\u8D25");
  }
  return document["cookie"]
}

go({
  "bts": ["1619445318.463|0|lRu", "WQDaBdfAdwz9FDJMCKuBXU%3D"],
  "chars": "vwZQEEHFyxidDakkkouBLW",
  "ct": "8f10d2ead700dd4b452946913e558fbf3b15a596",
  "ha": "sha1",
  "tn": "__jsl_clearance",
  "vt": "3600",
  "wt": "1500"
});