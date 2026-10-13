import 'package:flutter_test/flutter_test.dart';
import 'package:fixture_flutter/greeting.dart';

void main() {
  test('should greet by name', () {
    expect(greet('Ada'), 'Hello, Ada');
  });
}
