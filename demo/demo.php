<?php

// This file will be formatted

class Demo

{
  public function moveOut( $itemFromId, Message $message = null )
    {
    $case = $this->move_getCase( $itemFromId );
    return $this->sorter->moveOut( $itemFromId, $case, $message );
  }



  public function moveIn( $itemFromId, Message $message = null )
  {
    $case = $this->move_getCase( $itemFromId );
    return $this->sorter->moveIn( $itemFromId, $case );
  }


  public function moveAfter( $itemFromId, $itemToId, Message $message = null )
  {
    $case = $this->move_getCase( $itemFromId );
    return $this->sorter->moveAfter( $itemFromId, $itemToId, $case, $message );
  }

  public function getCurrent(  )
  {
    if( !$this->current )   {
      $this->current = $this->show( $_SESSION['cityid'] );
    }

    if( !$this->current )
    {
      $this->current = $this->show( 1 );
    }

    return $this->current;
  }

}