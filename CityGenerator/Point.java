public class Point {

	public int x;
	public int y;
	
	public Point() {
		x = -1;
		y = -1;
	}
	
	public Point(int theX, int theY) {
		x = theX;
		y = theY;
	}
	
	public String print() {
		return "(" + x + ", " + y + ")";
	}
	
}