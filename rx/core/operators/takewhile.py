from typing import Any, Callable

from rx.core import Observable, AnonymousObservable


def _take_while(predicate: Callable[[Any], Any]) -> Callable[[Observable], Observable]:
    def take_while(source: Observable) -> Observable:
        """Returns elements from an observable sequence as long as a
        specified condition is true. The element's index is used in the
        logic of the predicate function.

        Example:
            >>> take_while(source)

        Args:
            source: The source observable to take from.

        Returns:
            An observable sequence that contains the elements from the
            input sequence that occur before the element at which the
            test no longer passes.
        """

        def subscribe(observer, scheduler=None):
            running = True

            def on_next(value):
                nonlocal running

                with source.lock:
                    if not running:
                        return

                    try:
                        running = predicate(value)
                    except Exception as exn:
                        observer.on_error(exn)
                        return

                if running:
                    observer.on_next(value)
                else:
                    observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return take_while


def _take_while_indexed(predicate: Callable[[Any, int], Any]) -> Callable[[Observable], Observable]:
    def take_while_indexed(source: Observable) -> Observable:
        """Returns elements from an observable sequence as long as a
        specified condition is true. The element's index is used in the
        logic of the predicate function.

        Example:
            >>> take_while(source)

        Args:
            source: Source observable to take from.

        Returns:
            An observable sequence that contains the elements from the
            input sequence that occur before the element at which the
            test no longer passes.
        """

        def subscribe(observer, scheduler=None):
            running = True
            i = 0

            def on_next(value: Any) -> None:
                nonlocal running, i

                with source.lock:
                    if not running:
                        return

                    try:
                        running = predicate(value, i)
                    except Exception as exn:
                        observer.on_error(exn)
                        return
                    else:
                        i += 1

                if running:
                    observer.on_next(value)
                else:
                    observer.on_completed()

            return source.subscribe_(on_next, observer.on_error, observer.on_completed, scheduler)
        return AnonymousObservable(subscribe)
    return take_while_indexed
