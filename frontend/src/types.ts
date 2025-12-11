export interface Movie {
  movieId: number;
  title: string;
  overview?: string;
  tagline?: string;
  voteAverage?: number;
  voteCount?: number;
  releaseDate?: string;
  releaseYear?: number;
  language?: string;
  runtime?: number;
  budget?: number;
  weighted_score?: number;
  commentCount?: number;
  totalComments?: number;
  coverUrl?: string;
}

export interface Comment {
  commentId: number;
  commentText: string;
  timeStamp: string;
  userName: string;
}

export interface User {
  id: number;
  username: string;
  role: string;
}

export interface HomeData {
  top_rated: Movie[];
  random: Movie[];
  trending: Movie[];
  popular: Movie[];
}

export interface MovieDetail {
  movie: Movie;
  user_rating_average: number;
  user_rating: number | null;
  comments: Comment[];
}
