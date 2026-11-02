import 'package:flutter_test/flutter_test.dart';
import 'package:fixture_flutter/greeting.dart';

void main() {
  test('should greet with the generated word', () {
    expect(greet('Ada'), 'Hello, Ada');
  });
}
