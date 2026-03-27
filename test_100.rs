fn calculate(a: f64, op: char, b: f64) -> Option<f64> {
    match op {
        '+' => Some(a + b),
        '-' => Some(a - b),
        '*' => Some(a * b),
        '/' => if b == 0.0 { None } else { Some(a / b) },
        _ => None,
    }
}

fn main() {
    let ops = [(10.0, '+', 3.0), (10.0, '-', 3.0), (10.0, '*', 3.0), (10.0, '/', 3.0), (10.0, '/', 0.0)];
    for (a, op, b) in &ops {
        match calculate(*a, *op, *b) {
            Some(r) => {
                if r.fract() == 0.0 {
                } else {
                }
            }
        }
    }
}