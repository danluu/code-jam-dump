package snippets.algorithms
// Inspired by https://gist.github.com/happy4crazy/5489636

sealed trait Regex
case object Nil extends Regex
case object Empty extends Regex
case class Lit(c: Char) extends Regex
case class Union(left: Regex, right: Regex) extends Regex
case class Concat(right: Regex, left: Regex) extends Regex
case class Star(x: Regex) extends Regex

object RegexEngine{
  def success(x: Regex): Boolean = x match {
    case Nil => false
    case Empty => true
    case Lit(_) => false
    case Union(l, r) => success(l) || success(r)
    case Concat(l, r) => success(l) && success(r)
    case Star(_) => true
  }

  def step(x: Regex, c: Char): Regex = x match {
    case Nil => Nil
    case Empty => Nil
    case Lit(regexC) => 
      if (regexC == c) 
        Empty
      else 
        Nil
    case Union(l, r) => Union(step(l, c), step(r, c))
    case Concat(l, r) =>
      if (success(l)) 
        Union(Concat(step(l, c), r), step(r, c))
      else 
        Concat(step(l, c), r)
    case Star(regexX) => Concat(step(regexX, c), Star(regexX))
  }

  def run(x: Regex, s: String): Regex = s.foldLeft(x){(x,c) => step(x,c)}
  def matches(x: Regex, s: String): Boolean = success(run(x,s))

  def main(args: Array[String]) = {
    val a = Lit('a')
    val b = Lit('b')
    assert(matches(a, "a") == true)
    assert(matches(a, "aa") == false) //!
    val aStar = Star(a)
    assert(matches(aStar, "") == true)
    assert(matches(aStar, "a") == true)
    assert(matches(aStar, "aa") == true)
    val aPlus = Concat(a, aStar)
    assert(matches(aPlus, "") == false)
    assert(matches(aPlus, "a") == true)
    assert(matches(aPlus, "aa") == true) 
    val aStarb = Concat(aStar, b)
    assert(matches(aStarb, "b") == true)
    assert(matches(aStarb, "ab") == true)
    assert(matches(aStarb, "aab") == true)
    assert(matches(aStarb, "aaba") == false)
    val aStara = Concat(aStar, a)
    assert(matches(aStara, "a") == true)
    assert(matches(aStara, "aa") == true)
    assert(matches(aStara, "aaa") == true)
    val aStarab = Concat(aStara, b)
    assert(matches(aStarab, "ab") == true)
    assert(matches(aStarab, "aab") == true)
    assert(matches(aStarab, "aaab") == true)
    assert(matches(aStarab, "aaa") == false)
    val ab = Concat(a, b)
    val abStar = Star(ab)
    println(matches(abStar,"a"))
  }
}
